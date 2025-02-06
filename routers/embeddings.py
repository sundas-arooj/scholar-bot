from fastapi import APIRouter, UploadFile, HTTPException
from utils.pdf_processor import process_uploaded_file
from services.embeddings import store_embeddings, initialize_knowledge_base
import os

router = APIRouter()

@router.post("/upload-file")
async def upload_pdf(file: UploadFile):
    """
    Upload a PDF or Word file and create embeddings.
    If embeddings already exist, they will be deleted and recreated.
    """
    if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and Word documents are supported"
        )
    
    try:
        content = await file.read()
        doc_chunks = process_uploaded_file(content, file.filename)
        
        if not doc_chunks:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file"
            )
        
        result = store_embeddings(doc_chunks)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

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
