import time
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.config import config
from pinecone import Pinecone, ServerlessSpec
from app.utils.pdf_processor import process_pdf_document

pc = Pinecone(api_key=config.PINECONE_API_KEY)


def get_embeddings_function() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)

def create_pinecone_index():
    """
    Create or get existing Pinecone index and return it as a LangChain vector store.
    """
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    # Create index if it doesn't exist
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


def store_embeddings(doc_chunks: List[str]):
    """Store document chunks in Pinecone index"""
    embedding_function = get_embeddings_function()
    vector_store = PineconeVectorStore.from_texts(
        texts=doc_chunks,
        embedding=embedding_function,
        index_name=config.PINECONE_INDEX_NAME,
        text_key="text"
    )
    return vector_store

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
