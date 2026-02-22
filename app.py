from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler
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

from controller import message_spider_router, you_get_router, youtube_dl_router, telegram_sub_router
from dotenv import load_dotenv
from core.telegram_client import telegram_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：连接 Telegram 并加载缓存
    await telegram_manager.start()
    yield
    # 关闭时：断开连接
    await telegram_manager.stop()


load_dotenv()

app = FastAPI(lifespan=lifespan)

formatter = logging.Formatter('%(levelname)s - %(message)s')
file_handler = RotatingFileHandler(filename="app.log", maxBytes=1000000, backupCount=10)
file_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

origins = [
    "http://localhost:3000",
    "http://154.7.179.45:8081",
    "https://telegram.yxlm.cloud"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(message_spider_router)
app.include_router(you_get_router)
app.include_router(youtube_dl_router)
app.include_router(telegram_sub_router)


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

    uvicorn.run(app="app:app", host="localhost", port=8000, workers=4)
