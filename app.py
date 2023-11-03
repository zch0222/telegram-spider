from fastapi import FastAPI, Request
from controller import message_spider_router
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

app.include_router(message_spider_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="app:app", host="0.0.0.0", port=8000, workers=4)
