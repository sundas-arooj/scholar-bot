from fastapi import APIRouter
from routers import chat, embeddings

router = APIRouter()

router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(embeddings.router, prefix="/embeddings", tags=["Embeddings"])