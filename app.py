from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from controller import message_spider_router
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="app:app", host="0.0.0.0", port=8000, workers=4)
