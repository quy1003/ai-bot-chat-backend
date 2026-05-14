from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

project_root = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=project_root / ".env")

from app.lib.response import build_response
from app.routes.chat import router as chat_router

app = FastAPI()

# Allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return build_response(
        status=True,
        message="AI Backend Running",
        data=None,
    )

app.include_router(chat_router, prefix="/chat", tags=["Chat"])