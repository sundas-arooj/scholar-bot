# Building an Intelligent Document Q&A Bot with FastAPI and LangChain

In this tutorial, we'll walk through building ScholarBot - a powerful document Q&A assistant that lets users upload documents and have natural conversations about their content. We'll use FastAPI for the backend, LangChain for RAG (Retrieval Augmented Generation), and OpenAI's models for intelligence.

## Overview

ScholarBot allows users to:
1. Upload PDF/Word documents
2. Ask questions about the documents
3. Get accurate, context-aware responses
4. Have streaming conversations
5. Maintain context across chat sessions

## Tech Stack

- **Backend**: FastAPI
- **AI/ML**: LangChain, OpenAI GPT-4
- **Vector Store**: Pinecone
- **Frontend**: HTML, CSS, JavaScript
- **Document Processing**: PyPDF2, python-docx

## Step-by-Step Implementation

### 1. Project Structure

First, let's set up our project structure: 

```
scholar-bot/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   ├── chat.py
│   │   ├── document.py
│   │   └── embeddings.py

├── app/
│ ├── models/ # Pydantic models
│ ├── routers/ # API routes
│ ├── services/ # Business logic
│ ├── utils/ # Helper functions
│ ├── constants/ # Constants
│ ├── config.py # Configuration
│ └── main.py # FastAPI application
├── static/ # Frontend files
└── requirements.txt # Dependencies
```

### 2. Setting Up the Backend

#### FastAPI Application (main.py)

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers.router import router
app = FastAPI(title="ScholarBot")
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")
```

#### Document Processing (utils/pdf_processor.py)

```python
def process_uploaded_file(content: bytes, filename: str) -> list:
    """Process uploaded files and split into chunks"""
    if filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf_bytes(content)
    elif filename.lower().endswith(('.doc', '.docx')):
        text = extract_text_from_word_bytes(content)
    else:
        raise ValueError("Unsupported format")
    
    return split_text_into_chunks(text)
```

### 3. Implementing RAG with LangChain

The core of ScholarBot is its RAG implementation using LangChain. Here's how it works:

1. **Document Processing**:
   - Extract text from documents
   - Split into manageable chunks
   - Generate embeddings
   - Store in Pinecone vector database

2. **Question Answering**:
   - Embed user question
   - Retrieve relevant chunks
   - Generate context-aware response

#### Model Factory (services/model_factory.py)
```python
class ModelFactory:
    def get_default_chat_model(self) -> BaseChatModel:
        return self.get_chat_model(
            provider=ModelProvider.OPENAI,
            model_config={
                "model_name": "gpt-4-turbo-preview",
                "temperature": 0.7
            }
        )
```

### 4. Frontend Implementation

The frontend provides a clean, intuitive interface with two main components:

1. **Document Upload**:
```html
<div class="upload-section">
    <h2>Knowledge Base Upload</h2>
    <form id="uploadForm">
        <input type="file" id="fileInput" accept=".pdf,.doc,.docx" />
        <button type="submit">Upload Knowledge Base</button>
    </form>
</div>
```

2. **Chat Interface**:
```html
<div class="chat-container">
    <div class="chat-messages" id="chatMessages"></div>
    <div class="chat-input-section">
        <div class="stream-toggle">
            <input type="checkbox" id="streamToggle" checked>
            <span>Stream Response</span>
        </div>
        <input type="text" id="userInput" placeholder="Type your message..." />
        <button id="sendButton">Send</button>
    </div>
</div>
```

### 5. Key Features Implementation

#### Streaming Responses
```javascript
async function sendMessage(isStream) {
    if (isStream) {
        const response = await fetch('/chat/query', {
            // ... request config
        });
        const reader = response.body.getReader();
        while (true) {
            const {value, done} = await reader.read();
            if (done) break;
            // Process streaming response
        }
    }
}
```

#### Session Management
```python
@router.post("/chat/query")
async def chat_query(
    request: ChatRequest,
    session_id: Optional[str] = None
) -> ChatResponse:
    if not session_id:
        session_id = str(uuid4())
    # Process query with session context
    return ChatResponse(session_id=session_id, ...)
```

## Running the Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
OPENAI_API_KEY=your_key
PINECONE_API_KEY=your_key
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

4. Access at `http://localhost:8000`

## Advanced Features

### 1. Context-Aware Responses
ScholarBot maintains conversation history and uses it to provide more relevant responses:

```python
HISTORY_PROMPT = """
Given the conversation history and current question,
create a comprehensive search query that includes context
from previous messages.
"""
```

### 2. Vector Search
Using Pinecone for efficient similarity search:
```python
async def search_similar_chunks(query: str, top_k: int = 3):
    query_embedding = get_embedding(query)
    return pinecone_index.query(
        vector=query_embedding,
        top_k=top_k
    )
```

## Conclusion

ScholarBot demonstrates how to build a powerful document Q&A system using modern AI tools and frameworks. The combination of FastAPI, LangChain, and OpenAI provides a robust foundation for building intelligent document processing applications.

Key takeaways:
1. RAG provides more accurate responses than pure LLM
2. Streaming responses improve user experience
3. Session management enables contextual conversations
4. Vector search enables efficient document retrieval

The complete code is available on [GitHub](https://github.com/sundas-arooj/scholar-bot).