from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(content)
    text = "".join([page.extract_text() for page in reader.pages])
    return text

def split_text_into_chunks(text: str) -> list:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return text_splitter.split_text(text)
