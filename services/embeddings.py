import time
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from config import config
from pinecone import Pinecone, ServerlessSpec
from utils.pdf_processor import process_pdf_document

pc = Pinecone(api_key=config.PINECONE_API_KEY)

def get_embeddings_function() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)

def delete_pinecone_index():
    """Delete the Pinecone index if it exists."""
    try:
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if config.PINECONE_INDEX_NAME in existing_indexes:
            pc.delete_index(config.PINECONE_INDEX_NAME)
            # Wait for deletion to complete
            time.sleep(2)
        return True
    except Exception as e:
        print(f"Error deleting index: {str(e)}")
        return False

def create_pinecone_index():
    """Create or get existing Pinecone index and return it as a LangChain vector store."""
    try:
        # Create index if it doesn't exist
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if config.PINECONE_INDEX_NAME not in existing_indexes:
            pc.create_index(
                name=config.PINECONE_INDEX_NAME,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            
            # Wait for index to be ready
            while not pc.describe_index(config.PINECONE_INDEX_NAME).status["ready"]:
                time.sleep(1)

        # Create and return vector store
        embedding_function = get_embeddings_function()
        vector_store = PineconeVectorStore(
            index_name=config.PINECONE_INDEX_NAME,
            embedding=embedding_function,
            text_key="text"
        )
        
        return vector_store
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        return None

def store_embeddings(doc_chunks: List[str]) -> dict:
    """
    Store document chunks in Pinecone index.
    Deletes existing index if it exists and creates new embeddings.
    """
    try:
        delete_pinecone_index()
        
        if not create_pinecone_index():
            raise Exception("Failed to create index")

        # Create embeddings and store in Pinecone
        embedding_function = get_embeddings_function()
        PineconeVectorStore.from_texts(
            texts=doc_chunks,
            embedding=embedding_function,
            index_name=config.PINECONE_INDEX_NAME,
            text_key="text"
        )
        
        return {
            "status": "success",
            "message": f"Successfully processed and stored {len(doc_chunks)} chunks of text",
            "chunk_count": len(doc_chunks)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error storing embeddings: {str(e)}",
            "chunk_count": 0
        }

def initialize_knowledge_base(pdf_path: str):
    """Initialize the knowledge base from a PDF document."""
    try:
        # Process the PDF document
        chunks = process_pdf_document(pdf_path)
        if not chunks:
            raise Exception("No text chunks extracted from PDF")

        # Create embeddings and store in Pinecone
        embedding_function = get_embeddings_function()
        PineconeVectorStore.from_texts(
            texts=chunks,
            embedding=embedding_function,
            index_name=config.PINECONE_INDEX_NAME,
            text_key="text"
        )
        
        return {
            "status": "success",
            "message": f"Successfully processed and stored {len(chunks)} chunks of text",
            "chunk_count": len(chunks)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error initializing knowledge base: {str(e)}",
            "chunk_count": 0
        }
