"""Embedding service for generating vector embeddings using Gemini."""
from __future__ import annotations

from typing import Optional, List
import google.generativeai as genai

from app.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings using Google Gemini."""
    
    def __init__(self) -> None:
        self._enabled = False
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._model = settings.EMBEDDING_MODEL
                self._enabled = True
            except Exception as e:
                print(f"Failed to initialize EmbeddingService: {e}")
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a document text.
        
        Args:
            text: The text content to embed (will be truncated to 8000 chars)
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self._enabled:
            return []
        
        try:
            result = genai.embed_content(
                model=self._model,
                content=text[:8000],  # Limit content length
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            return []
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query.
        
        Uses retrieval_query task type for better search performance.
        
        Args:
            query: The search query to embed
            
        Returns:
            List of floats representing the query embedding vector
        """
        if not self._enabled:
            return []
        
        try:
            result = genai.embed_content(
                model=self._model,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Query embedding error: {e}")
            return []
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not self._enabled:
            return []
        
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            if embedding:
                embeddings.append(embedding)
        return embeddings


_embedding_singleton: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the singleton EmbeddingService instance."""
    global _embedding_singleton
    if _embedding_singleton is None:
        _embedding_singleton = EmbeddingService()
    return _embedding_singleton
