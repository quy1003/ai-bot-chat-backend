from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

project_root = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=project_root / ".env")

from app.lib.response import build_response
from app.lib.database import create_tables
from app.lib.models import Conversation, ChatMessage  # Import models for SQLAlchemy
from app.routes.chat import router as chat_router

app = FastAPI()

# Add CORS middleware FIRST before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
create_tables()

@app.get("/")
def root():
    return build_response(
        status=True,
        message="AI Backend Running",
        data=None,
    )

app.include_router(chat_router, prefix="/chat", tags=["Chat"])