from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from app.config import config
from app.constants.prompts import SYSTEM_PROMPT, HISTORY_PROMPT
from app.services.embeddings import create_pinecone_index

def create_chat_prompt():
    """Create a chat prompt template with system message and chat history."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "Context: {context}\nQuery: {input}"),
    ])
    return prompt

def create_history_aware_prompt():
    """Create a prompt template for the history-aware retriever."""
    return ChatPromptTemplate.from_messages([
        ("system", HISTORY_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

def format_docs(docs):
    """Format documents into a string."""
    return "\n\n".join(doc.page_content for doc in docs)

def query_bot(user_query: str, chat_history: ChatMessageHistory = None):
    """
    Query the chatbot with user input and optional chat history.
    
    Args:
        user_query (str): The user's question or input
        chat_history (ChatMessageHistory, optional): Previous chat history
        
    Returns:
        dict: Response containing the bot's answer and relevant context
    """
    try:
        # Initialize the vector store and retriever
        vector_store = create_pinecone_index()
        base_retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Initialize the chat model
        chat_model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=config.OPENAI_API_KEY, 
            temperature=0.7
        )

        # Create prompt templates
        chat_prompt = create_chat_prompt()
        is_chat_history_exists = chat_history and chat_history.messages

        # Create history-aware retriever if chat history exists
        if is_chat_history_exists:
            history_prompt = create_history_aware_prompt()
            retriever = create_history_aware_retriever(
                llm=chat_model,
                retriever=base_retriever,
                prompt=history_prompt
            )
        else:
            retriever = base_retriever

        # Create the document chain
        document_chain = create_stuff_documents_chain(
            llm=chat_model,
            prompt=chat_prompt,
            document_variable_name="context"
        )

        # Create the retrieval chain
        chain = create_retrieval_chain(
            retriever=retriever,
            combine_docs_chain=document_chain
        )

        # Run the chain
        response = chain.invoke({
            "input": user_query,
            "chat_history": chat_history.messages if is_chat_history_exists else []
        })

        # Extract the answer text from the response
        answer = str(response["answer"])
        
        # Update chat history with the new interaction
        if chat_history is not None:
            chat_history.add_user_message(user_query)
            chat_history.add_ai_message(answer)

        # Format the context and documents for the response
        context = [doc.page_content for doc in response.get("context", [])]
        source_documents = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in response.get("source_documents", [])
        ]

        return {
            "answer": answer,
            "context": context,
            "source_documents": source_documents
        }
        
    except Exception as e:
        print(f"Error in query_bot: {str(e)}")
        return {
            "answer": "I apologize, but I encountered an error processing your request.",
            "context": [],
            "source_documents": []
        }
