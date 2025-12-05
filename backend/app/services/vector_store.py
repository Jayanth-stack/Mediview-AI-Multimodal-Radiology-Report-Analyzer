"""Vector store service for RAG document retrieval."""
from __future__ import annotations

from typing import Optional, List, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document
from app.services.embeddings import EmbeddingService, get_embedding_service
from app.core.config import settings


class VectorStore:
    """Service for managing and searching the RAG knowledge base."""
    
    def __init__(self, session: Session, embedding_service: Optional[EmbeddingService] = None) -> None:
        self.session = session
        self.embeddings = embedding_service or get_embedding_service()
    
    def add_document(
        self,
        title: str,
        content: str,
        source: str,
        doc_type: str,
        doc_metadata: Optional[dict] = None
    ) -> Optional[int]:
        """Add a document to the knowledge base with its embedding.
        
        Args:
            title: Document title
            content: Full document content
            source: Source identifier (e.g., "radiopaedia", "acr")
            doc_type: Document type (e.g., "guideline", "case")
            metadata: Optional additional metadata
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.embeddings.enabled:
            print("EmbeddingService not enabled, storing without vector")
        
        embedding = self.embeddings.embed_text(content) if self.embeddings.enabled else None
        
        doc = Document(
            title=title,
            content=content,
            source=source,
            doc_type=doc_type,
            embedding=embedding,
            doc_metadata=doc_metadata
        )
        self.session.add(doc)
        self.session.commit()
        self.session.refresh(doc)
        return doc.id
    
    def search(self, query: str, limit: Optional[int] = None) -> List[Document]:
        """Find similar documents using vector similarity search.
        
        Args:
            query: Search query string
            limit: Maximum number of results (defaults to RAG_TOP_K from settings)
            
        Returns:
            List of matching Document objects ordered by similarity
        """
        limit = limit or settings.RAG_TOP_K
        
        if not self.embeddings.enabled:
            # Fallback to simple text search if embeddings unavailable
            return self._text_search(query, limit)
        
        query_embedding = self.embeddings.embed_query(query)
        if not query_embedding:
            return self._text_search(query, limit)
        
        try:
            # pgvector cosine distance search (lower = more similar)
            result = self.session.execute(
                select(Document)
                .where(Document.embedding.isnot(None))
                .order_by(Document.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            return list(result.scalars().all())
        except Exception as e:
            print(f"Vector search failed: {e}")
            return self._text_search(query, limit)
    
    def _text_search(self, query: str, limit: int) -> List[Document]:
        """Fallback text-based search using ILIKE."""
        try:
            search_term = f"%{query}%"
            result = self.session.execute(
                select(Document)
                .where(
                    Document.title.ilike(search_term) | 
                    Document.content.ilike(search_term)
                )
                .limit(limit)
            )
            return list(result.scalars().all())
        except Exception as e:
            print(f"Text search failed: {e}")
            return []
    
    def get_by_id(self, doc_id: int) -> Optional[Document]:
        """Retrieve a document by its ID."""
        return self.session.get(Document, doc_id)
    
    def delete(self, doc_id: int) -> bool:
        """Delete a document by ID."""
        doc = self.get_by_id(doc_id)
        if doc:
            self.session.delete(doc)
            self.session.commit()
            return True
        return False
    
    def list_all(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """List all documents with pagination."""
        result = self.session.execute(
            select(Document)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    def count(self) -> int:
        """Get total document count."""
        from sqlalchemy import func
        result = self.session.execute(select(func.count(Document.id)))
        return result.scalar() or 0


def get_vector_store(session: Session) -> VectorStore:
    """Factory function to create a VectorStore with the session."""
    return VectorStore(session)
