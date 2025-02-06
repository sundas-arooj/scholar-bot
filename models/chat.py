from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Document(BaseModel):
    """Model for document chunks returned from vector store"""
    page_content: str
    metadata: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    """Model for chat request"""
    session_id: Optional[str] = None
    message: str
    is_stream: bool = False

class ChatResponse(BaseModel):
    """Model for chat response"""
    session_id: str
    response: str
    context: List[str] = []
    source_documents: List[Document] = []

class MessageResponse(BaseModel):
    """Model for message response"""
    message: str 