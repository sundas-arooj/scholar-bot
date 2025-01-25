from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def split_text_into_chunks(text: str) -> list:
    """Split text into smaller chunks for processing."""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_text(text)
        return chunks
    except Exception as e:
        print(f"Error splitting text: {str(e)}")
        return []

def process_pdf_document(pdf_path: str) -> list:
    """Process a PDF document and return chunks of text."""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return []
    
    chunks = split_text_into_chunks(text)
    return chunks
