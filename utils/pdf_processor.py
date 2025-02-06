from PyPDF2 import PdfReader
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document

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

def extract_text_from_pdf_bytes(content: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        pdf_file = BytesIO(content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_word_bytes(content: bytes) -> str:
    """Extract text from Word document bytes."""
    try:
        doc_file = BytesIO(content)
        doc = Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from Word document: {str(e)}")
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

def process_uploaded_file(content: bytes, filename: str) -> list:
    """Process an uploaded file and return chunks of text."""
    try:
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf_bytes(content)
        elif filename.lower().endswith(('.doc', '.docx')):
            text = extract_text_from_word_bytes(content)
        else:
            raise ValueError("Unsupported file format")
        
        if not text:
            return []
        
        return split_text_into_chunks(text)

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []
