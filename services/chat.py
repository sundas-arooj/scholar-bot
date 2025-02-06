from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.callbacks import AsyncIteratorCallbackHandler
from constants.prompts import SYSTEM_PROMPT, HISTORY_PROMPT
from services.embeddings import create_pinecone_index
from services.model_factory import ModelFactory, ModelProvider
from typing import Optional, Dict, Any, AsyncGenerator, Union
import asyncio

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

async def query_bot(
    user_query: str, 
    chat_history: ChatMessageHistory = None,
    model_provider: ModelProvider = ModelProvider.OPENAI,
    model_config: Optional[Dict[str, Any]] = None,
    is_stream: bool = False,
    session_id: str = None
) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
    """
    Query the chatbot with user input and optional chat history.
    
    Args:
        user_query (str): The user's question or input
        chat_history (ChatMessageHistory, optional): Previous chat history
        model_provider (ModelProvider): The model provider to use
        model_config (Dict[str, Any], optional): Model-specific configuration
        is_stream (bool): Whether to stream the response
        
    Returns:
        Union[Dict[str, Any], AsyncGenerator[str, None]]: Response containing the bot's answer or stream
    """
    try:
        # Initialize callback handler for streaming if needed
        callback_handler = AsyncIteratorCallbackHandler() if is_stream else None
        
        # Initialize the vector store and retriever
        vector_store = create_pinecone_index()
        base_retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Get chat model with streaming configuration if needed
        chat_model = ModelFactory().get_chat_model(
            provider=model_provider,
            model_config={
                **(model_config or {}),
                "streaming": is_stream,
                "callbacks": [callback_handler] if callback_handler else None,
            }
        )

        # Create prompt templates
        qa_prompt = create_chat_prompt()
        
        contextualize_q_prompt = create_history_aware_prompt()

        # Create history-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            chat_model, 
            base_retriever, 
            contextualize_q_prompt
        )

        # Create the QA chain
        question_answer_chain = create_stuff_documents_chain(
            chat_model,
            qa_prompt,
            document_variable_name="context",
        )

        # Create the RAG chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain
        )

        # Create a wrapper for chat history management
        def get_conversation_history(session_id: str) -> ChatMessageHistory:
            return chat_history or ChatMessageHistory()

        chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history=get_conversation_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        # Configure the chain with streaming and include source documents
        configured_chain = chain.with_config(
            {
                "configurable": {
                    "stream": is_stream,
                    "callbacks": [callback_handler] if callback_handler else None,
                },
                "run_name": "ScholarBotRAGChain"
            }
        )

        if is_stream:
            async def stream_and_save():
                try:
                    stream = configured_chain.astream(
                        {
                            "input": user_query,
                        },
                        {
                            "configurable": {
                                "session_id": session_id,
                                "stream": is_stream,
                                "callbacks": [callback_handler] if callback_handler else None,
                            },
                            "run_name": "ScholarBotRAGChain"
                        }
                    )
                    
                    complete_response = []
                    async for chunk in stream:
                        if 'answer' in chunk:
                            complete_response.append(chunk['answer'])
                            yield chunk['answer']
                            await asyncio.sleep(0.05)
                    
                    if complete_response and chat_history is not None:
                        full_response = "".join(complete_response)
                        chat_history.add_user_message(user_query)
                        chat_history.add_ai_message(full_response)

                except Exception as e:
                    print(f"Error in streaming response: {str(e)}")
                    yield "I apologize, but I encountered an error processing your request."

            return stream_and_save()
        else:
            # Non-streaming response with session_id
            response = await configured_chain.ainvoke(
                {
                    "input": user_query,
                },
                {
                    "configurable": {
                        "session_id": session_id
                    }
                }
            )

            answer = str(response.get("answer", ""))
            
            if chat_history is not None:
                chat_history.add_user_message(user_query)
                chat_history.add_ai_message(answer)

            return {
                "answer": answer,
                "context": [doc.page_content for doc in response.get("context", [])],
                "source_documents": [
                    {"page_content": doc.page_content, "metadata": doc.metadata}
                    for doc in response.get("source_documents", [])
                ]
            }
        
    except Exception as e:
        error_msg = f"Error in query_bot: {str(e)}"
        print(error_msg)
        if is_stream:
            async def error_generator():
                yield "I apologize, but I encountered an error processing your request."
            return error_generator()
        else:
            return {
                "answer": "I apologize, but I encountered an error processing your request.",
                "context": [],
                "source_documents": []
            }
