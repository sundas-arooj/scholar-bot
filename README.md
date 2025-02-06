# ScholarBot

ScholarBot is an intelligent document Q&A assistant that allows users to upload documents (PDF/Word) and ask questions about their content. Built with FastAPI and LangChain, it uses advanced language models and vector search to provide accurate, context-aware responses based on the uploaded documents.

## Key Features

- **Document Q&A**: Ask questions about your uploaded documents and get accurate answers
- **Document Processing**: Upload and analyze PDF and Word documents
- **Context-Aware**: Responses are based on the actual content of your documents
- **Real-time Streaming**: Stream responses as they're generated with toggle option
- **Vector Search**: Efficient document retrieval using Pinecone
- **Modern UI**: Clean, responsive dark-themed interface
- **Session Management**: Maintains conversation context

### Learn more about it in the following blog post:
[Building ScholarBot: An Intelligent Document Q&A Assistant with FastAPI and LangChain](https://medium.com/@sundasarooj/building-scholarbot-an-intelligent-document-q-a-assistant-with-fastapi-rag-and-langchain)

![ScholarBot: AI-Powered Document Q&A Assistant](./scholar-bot.png?raw=true "ScholarBot")

## Prerequisites

- Python 3.9+
- OpenAI API Key
- Pinecone API Key
- Virtual Environment (recommended)

## Installation and Setup

1. Clone the repository:
```
git clone https://github.com/sundas-arooj/scholar-bot.git
cd scholar-bot
```

2. Create a virtual environment: 
```
python -m venv venv
```

3. Activate the virtual environment:
    - On Windows: 
    ```
    venv\Scripts\activate
    ```
    - On macOS and Linux:
    ```
    source venv/bin/activate
    ```

4. Install the required dependencies:
    - On Windows:
    ```
    pip install -r requirements.txt
    ```
    - On macOS and Linux:
    ```
    pip install -r requirements.txt -r requirements-unix.txt
    ```

5. Set up environment variables:
Create a .env file in the root directory and add the following variables:
```
OPENAI_API_KEY=<your-openai-api-key>
PINECONE_API_KEY=<your-pinecone-api-key>
```

## Running the FastAPI Application

1. Run the application:
```
uvicorn main:app --reload
```

2. Access the application:
    - Open your browser and navigate to `http://localhost:8000` to start using Scholar Bot.
    - Go to `http://127.0.0.1:8000/docs` to access the Swagger UI documentation and test the API endpoints.

## How to Use

1. **Upload Documents**:
   - Click the "Choose File" button to select a PDF or Word document
   - Click "Upload Knowledge Base" to process the document
   - Wait for confirmation that the document has been processed

2. **Ask Questions**:
   - Type your question about the uploaded document in the chat input
   - Toggle streaming responses on/off using the switch
   - Get answers based on the document's content
   - Continue the conversation with follow-up questions

## Features in Detail

### Document Processing
- Support for PDF and Word documents
- Automatic text extraction and chunking
- Vector embedding generation for efficient search
- Document content stored in Pinecone vector database

### Chat Interface
- Real-time streaming responses
- Context-aware conversations based on document content
- Toggle between streaming/non-streaming responses
- Modern dark-themed UI
- Session-based chat history

### Vector Search
- Efficient similarity search using Pinecone
- Context-aware retrieval of relevant document sections
- RAG (Retrieval Augmented Generation) for accurate answers
- History-aware document retrieval

## API Documentation

Access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Chat Endpoints
- `POST /chat/query`: Send a question and get response from documents
  - Supports both streaming and non-streaming responses
  - Maintains chat history per session
  - Returns relevant context from documents

### Document Endpoints
- `POST /embeddings/upload-file`: Upload and process documents
  - Supports PDF and Word formats
  - Returns chunk count and processing status

## Development

The application uses:
- FastAPI for the backend
- LangChain for RAG and chat functionality
- Pinecone for vector storage
- OpenAI's models for embeddings and chat

## Contribution
Contributions are welcome! Please submit a pull request or open an issue to suggest improvements or add new features.
