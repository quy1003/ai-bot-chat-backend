# AI Bot Chat Demo - Chat History Integration

## Tổng Quan Hệ Thống

Ứng dụng chat AI được xây dựng với **Frontend (Nuxt 4)** và **Backend (FastAPI)**, hỗ trợ lưu trữ lịch sử trò chuyện toàn bộ context. AI sử dụng mô hình Groq LLaMA và hoạt động **stateless** - nghĩa là mỗi yêu cầu đều gửi kèm toàn bộ context từ đầu trò chuyện.

---

## 1. Kiến Trúc Hệ Thống

### Stack Công Nghệ
- **Frontend**: Nuxt 4.4.5 + Vue 3 + TailwindCSS + Pinia (State Management)
- **Backend**: FastAPI 0.104.1 + SQLAlchemy 2.0.23 + SQLite
- **AI Model**: Groq API (llama-3.1-8b-instant)
- **Real-time**: Server-Sent Events (SSE) để streaming response

### Cơ Sở Dữ Liệu
```
chat_history.db (SQLite)
├── conversations (Bảng lưu trữ trò chuyện)
│   ├── id (Primary Key)
│   ├── title (Tiêu đề trò chuyện)
│   ├── created_at (Thời gian tạo)
│   └── updated_at (Thời gian cập nhật cuối)
│
└── chat_messages (Bảng lưu trữ tin nhắn)
    ├── id (Primary Key)
    ├── conversation_id (Foreign Key)
    ├── role ('user' hoặc 'bot')
    ├── content (Nội dung tin nhắn)
    └── created_at (Thời gian tạo)
```

## 2. Quy Trình Full Circle: Từ Đầu Đến Cuối

```
┌─ USER INTERACTION ─┐
│                    │
│  1. User mở app    │
│     → Frontend fetch danh sách conversations
│        → Backend trả list từ database
│        → Pinia store cập nhật
│        → UI hiển thị sidebar
│                    │
│  2. User click "New Chat"
│     → Frontend POST /conversations
│        → Backend tạo row mới
│        → Pinia store thêm vào list
│        → UI chuyển sang chat area trống
│                    │
│  3. User nhập message + Send
│     → Frontend gọi sendMessage action
│        → Optimistic update: hiển thị user msg ngay
│        → POST /conversations/{id}/send
│        → Backend: lưu user message
│                    │
│  4. Backend lấy TOÀN BỘ context
│     → Query database: ALL messages
│     → Format cho Groq API
│     → Gọi Groq API với full history
│                    │
│  5. Groq API sinh response
│     → AI đọc full conversation history
│     → Hiểu context
│     → Sinh response
│     → Gửi từng chunk
│                    │
│  6. Backend stream response
│     → Nhận chunk từ Groq
│     → Gửi về frontend via SSE
│     → Accumulate full response
│                    │
│  7. Frontend nhận SSE chunks
│     → Parse SSE format
│     → Accumulate vào botMessage.content
│     → Vue reactivity tự update UI
│     → User thấy response streaming
│                    │
│  8. Backend lưu bot response
│     → Lưu full accumulated response
│     → Insert row vào chat_messages
│     → Conversation updated_at cập nhật
│                    │
│  9. User thấy full response
│     → Message hiển thị trong chat area
│     → Message lưu trong database
│     → Nếu page refresh → vẫn thấy message (persistence)
│                    │
│ 10. User gửi message tiếp
│     → Repeat từ step 3
│     → Backend lại gửi TOÀN BỘ context (cả message mới)
│     → AI hiểu context đầy đủ
│
└────────────────────┘
```

---

## 3. Khởi Động Ứng Dụng

### Backend
```bash
cd ai-bot-chat-demo/ai-bot-chat-backend
python -m uvicorn app.main:app --port 8000
```

### Frontend
```bash
cd ai-bot-chat-demo/ai-bot-chat-frontend
npm run dev  # hoặc pnpm dev
# Truy cập: http://localhost:3001
```

---

## 4. Structure chính

### Backend
- `app/main.py` - FastAPI entry point
- `app/routes/chat.py` - Endpoints logic
- `app/lib/models.py` - SQLAlchemy models
- `app/lib/database.py` - Database config
- `app/schemas/chat_schema.py` - Pydantic schemas

### Frontend
- `stores/chat.ts` - Pinia store (state management)
- `app/components/ChatBox.vue` - Main chat UI
- `nuxt.config.ts` - Nuxt config

### Database
- `chat_history.db` - SQLite database (auto-created)

---

## 5. Tóm Tắt Điểm Chính

| Khía Cạnh | Chi Tiết |
|-----------|---------|
| **Architecture** | Client-Server (Frontend-Backend) |
| **State Management** | Pinia store (centralized) |
| **Real-time** | Server-Sent Events (SSE streaming) |
| **Database** | SQLite with SQLAlchemy ORM |
| **AI Integration** | Groq API (stateless) |
| **Context Sharing** | Toàn bộ conversation history gửi mỗi request |
| **Persistence** | Mỗi message lưu vào database |
| **Scaling** | Stateless design → dễ scale |
