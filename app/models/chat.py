from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str
    context: List[str] = []
    source_documents: List[Dict[str, Any]] = []

class MessageResponse(BaseModel):
    message: str 