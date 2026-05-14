# AI PDF Chatbot

Một dự án AI Chatbot sử dụng RAG (Retrieval Augmented Generation) để chat với nội dung PDF bằng AI.

Project được xây dựng nhằm học và thực hành:

- AI-powered applications
- RAG architecture
- Vector Database
- Embeddings
- Semantic Search
- AI Agents
- MCP (Model Context Protocol)

---

# 🚀 Tech Stack

## Frontend

- Vue 3
- Nuxt 3
- TailwindCSS
- TypeScript

## Backend

- FastAPI
- Python

## AI / LLM

- Gemini API (Free Tier)
- Ollama (Local Models - Optional)

## Database

- PostgreSQL
- pgvector

## Storage

- Local Storage
- AWS S3 (future)

## Deploy

- Vercel
- Railway / Render
- AWS Free Tier

---

# 📌 Features

## V1

- Upload PDF
- Parse PDF content
- AI Chat
- Semantic Search
- RAG pipeline
- Streaming AI response

## V2

- Multiple PDFs
- Chat history
- Markdown rendering
- Citations / Sources

## V3

- Authentication
- Cloud storage
- Conversation memory
- AI Agent tools

## V4

- MCP Integration
- Tool Calling
- Web Search
- Multi-agent workflows

---

# 🧠 System Architecture

```txt
Frontend (Nuxt 3)
        ↓
FastAPI Backend
        ↓
PDF Upload
        ↓
PDF Parsing
        ↓
Chunking
        ↓
Embeddings
        ↓
Store vectors in pgvector
        ↓
User Question
        ↓
Similarity Search
        ↓
Retrieve Related Chunks
        ↓
LLM (Gemini / Ollama)
        ↓
AI Response
```
Run APP:
uvicorn app.main:app --reload