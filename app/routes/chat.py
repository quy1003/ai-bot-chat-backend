import os

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from groq import Groq

from app.lib.constants import GROQ_MODEL, RESPONSE_STATUS_SUCCESS
from app.lib.response import build_response
from app.schemas.chat_schema import ChatRequest

router = APIRouter()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@router.post("/")
def ask_gemini_stream(request: ChatRequest):
    # Fake streaming: split reply into chunks and yield as SSE
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": request.message}],
    )
    reply = response.choices[0].message.content

    def event_stream():
        chunk_size = 20
        for i in range(0, len(reply), chunk_size):
            chunk = reply[i:i+chunk_size]
            yield f"data: {chunk}\n\n"
        yield "data: [END]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")