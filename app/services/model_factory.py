from typing import Optional, Dict, Any
from enum import Enum
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_community.llms import LlamaCpp
from langchain.chat_models.base import BaseChatModel
from app.config import config

class ModelProvider(str, Enum):
    """Supported model providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    LLAMA = "llama"

class ModelFactory:
    """Factory class for creating different language models"""
    
    def __init__(self):
        self.MODEL_CREATORS = {
            ModelProvider.OPENAI: self._create_openai_model,
            # ModelProvider.GEMINI: self._create_gemini_model,
            # ModelProvider.LLAMA: self._create_llama_model
        }
    
    def _create_openai_model(
        self,
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        **kwargs
    ) -> ChatOpenAI:
        """Create OpenAI chat model"""
        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=kwargs.get('api_key') or config.OPENAI_API_KEY
        )
    
    # def _create_gemini_model(
    #     self,
    #     model_name: str = "gemini-pro",
    #     temperature: float = 0.7,
    #     **kwargs
    # ) -> ChatGoogleGenerativeAI:
    #     """Create Google Gemini chat model"""
    #     return ChatGoogleGenerativeAI(
    #         model=model_name,
    #         temperature=temperature,
    #         google_api_key=kwargs.get('api_key') or config.GEMINI_API_KEY
    #     )
    
    # def _create_llama_model(
    #     self,
    #     model_path: str,
    #     temperature: float = 0.7,
    #     **kwargs
    # ) -> LlamaCpp:
    #     """Create Llama chat model"""
    #     return LlamaCpp(
    #         model_path=model_path,
    #         temperature=temperature,
    #         **kwargs
    #     )

    def get_chat_model(
        self,
        provider: ModelProvider = ModelProvider.OPENAI,
        model_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> BaseChatModel:
        """
        Get a chat model instance based on the specified provider and configuration.
        
        Args:
            provider (ModelProvider): The model provider to use
            model_config (Dict[str, Any], optional): Model-specific configuration
            **kwargs: Additional arguments for model creation
            
        Returns:
            BaseChatModel: Configured chat model instance
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider not in self.MODEL_CREATORS:
            raise ValueError(f"Unsupported model provider: {provider}")
        
        model_config = model_config or {}
        creator = self.MODEL_CREATORS[provider]
        return creator(**model_config, **kwargs)

    def get_default_chat_model(self) -> BaseChatModel:
        """Get the default chat model configuration (OpenAI)"""
        return self.get_chat_model(
            provider=ModelProvider.OPENAI,
            model_config={
                "model_name": "gpt-4-turbo-preview",
                "temperature": 0.7
            }
        ) 