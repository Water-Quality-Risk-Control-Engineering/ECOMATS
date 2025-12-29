"""
DashScope Embedding Function.
Provides embedding support for CrewAI memory system.
"""

import os
import numpy as np
from chromadb.api.types import EmbeddingFunction as ChromaEmbeddingFunction
from crewai.rag.embeddings.providers.custom.embedding_callable import CustomEmbeddingFunction
from crewai.rag.core.types import Documents, Embeddings
from openai import OpenAI


class DashScopeEmbeddingFunction(CustomEmbeddingFunction, ChromaEmbeddingFunction):
    """
    Use OpenAI SDK to call DashScope Embedding API.
    
    Inherits from both ChromaDB and CrewAI base classes to satisfy Pydantic validation.
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('QWEN_API_KEY'),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "text-embedding-v2"
        
    def __call__(self, input: Documents) -> Embeddings:
        """
        Convert text to embedding vectors.
        
        Args:
            input: List of strings (Documents = list[str])
            
        Returns:
            Embeddings: List of numpy arrays (list[np.ndarray])
        """
        try:
            # DashScope text-embedding-v2 limit: 1-2048 characters
            MAX_LENGTH = 2048
            truncated_input = [
                text[:MAX_LENGTH] if len(text) > MAX_LENGTH else text
                for text in input
            ]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=truncated_input
            )
            # Return list of numpy arrays
            embeddings = [
                np.array(item.embedding, dtype=np.float32) 
                for item in response.data
            ]
            return embeddings
        except Exception as e:
            print(f"⚠️ DashScope Embedding Error: {e}")
            # Return zero vectors as default (dimension 1536, consistent with v2)
            return [np.zeros(1536, dtype=np.float32) for _ in range(len(input))]


def create_dashscope_embedder():
    """
    Create DashScope Embedding class for CrewAI memory system.
    
    Returns:
        class: DashScopeEmbeddingFunction class (not instance)
    """
    return DashScopeEmbeddingFunction
