from fastapi import APIRouter, UploadFile, HTTPException
from app.utils.pdf_processor import extract_text_from_pdf, split_text_into_chunks
from app.services.embeddings import store_embeddings, initialize_knowledge_base
import os

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile):
    content = await file.read()
    text = extract_text_from_pdf(content)
    doc_chunks = split_text_into_chunks(text)
    store_embeddings(doc_chunks)
    return {"message": "PDF processed and embeddings stored successfully."}

@router.post("/initialize-knowledge-base")
async def init_knowledge_base():
    """Initialize the knowledge base from the Seq2Seq PDF."""
    pdf_path = os.path.join("static", "Seq2Seq.pdf")
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=404,
            detail="PDF file not found in static folder"
        )
    
    result = initialize_knowledge_base(pdf_path)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=500,
            detail=result["message"]
        )
    
    return result
