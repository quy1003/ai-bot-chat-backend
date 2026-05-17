import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.lib.constants import GROQ_MODEL
from app.lib.database import get_db
from app.lib.models import Conversation, ChatMessage
from app.schemas.chat_schema import (
    ChatRequest,
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    ChatMessageResponse,
)

router = APIRouter()


def get_groq_client():
    """Lazy load Groq client"""
    import sys
    from groq import Groq
    try:
        # Try standard initialization
        return Groq(api_key=os.getenv("GROQ_API_KEY"))
    except TypeError as e:
        # Handle compatibility issues with httpx
        if "proxies" in str(e):
            # If proxies argument is the issue, try with explicit http_client
            import httpx
            client = httpx.Client(timeout=None)
            return Groq(api_key=os.getenv("GROQ_API_KEY"), http_client=client)
        raise


def generate_conversation_title(message: str) -> str:
    """Generate a conversation title from the first user message using Groq"""
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a short conversation title (max 50 characters) from this message. Only respond with the title, nothing else.\n\nMessage: {message}"
                }
            ],
            temperature=0.7,
            max_tokens=100
        )
        title = response.choices[0].message.content.strip()
        # Ensure title is not too long
        return title[:50] if len(title) > 50 else title
    except Exception as e:
        print(f"Error generating title: {e}")
        # Fallback: use first 50 chars of message
        return message[:50] + "..." if len(message) > 50 else message


# ============= CONVERSATION ENDPOINTS =============


@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    conversation = Conversation(title=request.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/conversations", response_model=List[ConversationListResponse])
def get_conversations(db: Session = Depends(get_db)):
    """Get all conversations (sorted by most recent)"""
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation deleted successfully"}


# ============= MESSAGE ENDPOINTS =============


@router.post("/conversations/{conversation_id}/send")
def send_message_stream(
    conversation_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send message and get streaming response"""
    # Verify conversation exists
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Check if this is the first message in conversation
    message_count_before = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).count()
    is_first_message = message_count_before == 0

    # Save user message
    user_message = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()

    # If this is the first message, generate a title for the conversation
    if is_first_message:
        try:
            generated_title = generate_conversation_title(request.message)
            conversation.title = generated_title
            db.commit()
        except Exception as e:
            print(f"Error updating conversation title: {e}")

    # Get all messages from this conversation for context
    all_messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at.asc()).all()

    # Format messages for Groq API (convert "bot" role to "assistant" for Groq compatibility)
    formatted_messages = [
        {"role": "assistant" if msg.role == "bot" else msg.role, "content": msg.content} for msg in all_messages
    ]

    # Call Groq API
    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=formatted_messages,
        stream=True,
    )

    def event_stream():
        full_response = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield f"data: {content}\n\n"
                full_response += content

        yield "data: [END]\n\n"

        # Save bot message after streaming is complete
        try:
            bot_message = ChatMessage(
                conversation_id=conversation_id,
                role="bot",
                content=full_response
            )
            # Create new session for saving (since we're in streaming)
            db.add(bot_message)
            db.commit()
        except Exception as e:
            print(f"Error saving bot message: {e}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


# ============= LEGACY ENDPOINT (for backward compatibility) =============


@router.post("/")
def ask_gemini_stream(request: ChatRequest):
    """Legacy endpoint - sends message without conversation history"""
    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": request.message,
            }
        ],
        stream=True,
    )

    def event_stream():
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield f"data: {content}\n\n"

        yield "data: [END]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )