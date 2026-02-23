from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import StreamingResponse
import subprocess

from exception.business_exception import BusinessException
from model import ResData
import time
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from controller import message_spider_router, you_get_router, youtube_dl_router, telegram_sub_router, auth_controller, yt_dlp_controller
from dotenv import load_dotenv
from core.telegram_client import telegram_manager
from core.polling_service import polling_service
from middleware.auth_middleware import AuthMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import CORS_ORIGINS

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：连接 Telegram 并加载缓存
    await telegram_manager.start()
    # 启动轮询服务
    await polling_service.start()
    
    yield
    
    # 关闭时：停止轮询服务
    await polling_service.stop()
    # 断开连接
    await telegram_manager.stop()


from core.log import get_logger

load_dotenv()

app = FastAPI(lifespan=lifespan)

logger = get_logger()
logger.info("Application starting...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(message_spider_router)
app.include_router(you_get_router)
app.include_router(youtube_dl_router)
app.include_router(telegram_sub_router)
app.include_router(auth_controller.auth_router)
app.include_router(yt_dlp_controller.yt_dlp_router)

# Register Auth Middleware (It should be added after CORS middleware usually, 
# but FastAPI executes middlewares in reverse order of addition. 
# So if we want Auth to run after CORS (which handles preflight), 
# we should add Auth BEFORE CORS? 
# No, Starlette BaseHTTPMiddleware runs in the order added to the list if using `add_middleware`.
# But `app.add_middleware` appends to the list which is processed wrapper-style.
# The last added middleware is the first to receive the request.
# So we want CORS to handle OPTIONS first. So CORS should be added LAST (which means first in code execution).
# Wait, `add_middleware` adds to the top of the stack.
# Request -> Middleware N -> ... -> Middleware 1 -> App
# So if we want CORS to run first, we should add it LAST.
# Currently CORS is added. Let's add Auth middleware.
# We want: Request -> CORS -> Auth -> App
# So we should add Auth first, then CORS.
# But CORS is already added. 
# Let's just add Auth middleware using app.add_middleware.
# Since we want Auth to verify cookies, and CORS handles Access-Control headers.
# If Auth fails, we still want CORS headers present so frontend can read the error.
# So CORS should wrap Auth.
# Meaning CORS should be added AFTER Auth in code (because of LIFO stack).
# But here CORS is already added. So if I add Auth now, Auth will be outside CORS?
# Request -> Auth -> CORS -> App
# If Auth returns 401, CORS headers might be missing if CORS is inner.
# So we need Auth to be INNER to CORS.
# Request -> CORS -> Auth -> App
# So Auth should be added BEFORE CORS in the code? No, `add_middleware` puts it on top.
# So if I call `app.add_middleware(Auth)` NOW, it becomes the outermost.
# To make it inner, it should have been added BEFORE CORS.
# Let's try to add it. If CORS issues arise, we can reorder.
# Actually, for `BaseHTTPMiddleware`, the order is tricky.
# Let's just add it and see. Usually we want CORS outermost.
# So we should add Auth, then CORS. 
# Since CORS is already there, I should probably insert Auth before CORS or re-add CORS?
# Let's simply add it.

app.add_middleware(AuthMiddleware)


# 1. 处理自定义业务异常 (BusinessException)
#    场景：代码中主动 raise BusinessException("密码错误")
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.info(f"业务异常: {exc.msg}")
    # 业务异常通常返回 HTTP 200，但在 body 的 code 中体现为 0 (失败)
    return JSONResponse(
        status_code=200,
        content=ResData.error(exc.msg)
    )


# 2. 处理 HTTP 异常 (StarletteHTTPException)
#    场景：404 Not Found, 401 Unauthorized, 或者是 fastapi 内置抛出的 http 错误
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP错误: {request.url.path} - {exc.detail}")
    # 保持原有的 HTTP 状态码 (如 404)，但 Body 使用统一格式
    return JSONResponse(
        status_code=200,
        content=ResData.error(str(exc.detail))
    )


# 3. 处理参数校验错误 (RequestValidationError)
#    场景：前端传参类型错误、必填项缺失 (422 错误)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 提取 Pydantic 的错误详情
    errors = exc.errors()
    # 取第一条错误信息拼接，或者返回 "参数校验失败"
    error_msg = f"参数错误: {errors[0]['loc'][-1]} - {errors[0]['msg']}" if errors else "参数校验失败"

    logger.warning(f"参数校验失败: {request.url.path} - {error_msg}")

    return JSONResponse(
        status_code=200,
        content=ResData.error(error_msg)
    )


# 4. 处理所有其他未知异常 (Exception)
#    场景：代码 Bug、数据库连接断开、空指针等 (500 错误)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 记录完整堆栈信息 (exc_info=True)，这对于排查 Bug 至关重要
    logger.error(f"系统内部错误: {request.url.path} - {exc}", exc_info=True)

    return JSONResponse(
        status_code=200,
        content=ResData.error("服务器繁忙，请稍后重试")  # 不向前台展示具体代码错误，防止泄露敏感信息
    )

@app.post("/restart")
def restart():
    command = "pkill -f 'uvicorn' && nohup uvicorn main:app --host 0.0.0.0 --port 8000 &"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        return ResData.error("重启失败")
    else:
        return ResData.success("重启成功")


async def get_status():
    while True:
        print("RUNNING")
        yield 'id: "{}"\nevent: "message"\ndata: {}\n\n'.format(int(time.time()),
                                                                json.dumps(ResData.success("RUNNING")))

        await asyncio.sleep(2)


@app.get("/status")
def status():
    headers = {
        # 设置返回数据类型是SSE
        'Content-Type': 'text/event-stream',
        # 保证客户端的数据是新的
        'Cache-Control': 'no-cache',
    }
    return StreamingResponse(get_status(), headers=headers)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="app:app", host="localhost", port=8000, workers=1)
