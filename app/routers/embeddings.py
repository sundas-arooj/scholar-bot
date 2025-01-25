from fastapi import APIRouter, UploadFile
from app.utils.pdf_processor import extract_text_from_pdf, split_text_into_chunks
from app.services.embeddings import store_embeddings

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile):
    content = await file.read()
    text = extract_text_from_pdf(content)
    doc_chunks = split_text_into_chunks(text)
    store_embeddings(doc_chunks)
    return {"message": "PDF processed and embeddings stored successfully."}
