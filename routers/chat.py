from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict
from uuid import uuid4
from langchain_community.chat_message_histories import ChatMessageHistory
from services.chat import query_bot
from models.chat import ChatRequest, ChatResponse, MessageResponse, Document

router = APIRouter()

# Store chat histories in memory (consider using Redis or a database for production)
sessions: Dict[str, ChatMessageHistory] = {}

@router.post("/query", response_model=ChatResponse)
async def query_chatbot(chat_request: ChatRequest):
    """
    Handle chat queries with session management.
    
    Args:
        chat_request: Contains message and optional session_id
    """
    try:
        # Generate session_id if not provided
        session_id = chat_request.session_id or str(uuid4())
        
        # Get or create new chat history for this session
        if session_id not in sessions:
            sessions[session_id] = ChatMessageHistory()
        
        chat_history = sessions[session_id]

        if chat_request.is_stream:
            response = StreamingResponse(
                await query_bot(
                    user_query=chat_request.message,
                    chat_history=chat_history,
                    is_stream=True,
                    session_id=session_id
                ),
                media_type='text/event-stream'
            )
            
            response.headers["X-Session-ID"] = session_id
            
            return response

        # Query the bot with chat history
        response = await query_bot(
            user_query=chat_request.message,
            chat_history=chat_history,
            session_id=session_id
        )
        
        return ChatResponse(
            session_id=session_id,
            response=response["answer"],
            context=response["context"],
            source_documents=[Document(**doc) for doc in response["source_documents"]]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.delete("/session/{session_id}", response_model=MessageResponse)
async def clear_chat_history(session_id: str):
    """Clear chat history for a given session"""
    if session_id in sessions:
        del sessions[session_id]
    return MessageResponse(message=f"Session {session_id} cleared")
