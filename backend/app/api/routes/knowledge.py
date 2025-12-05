"""Knowledge base API routes for RAG document management."""
from __future__ import annotations

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.vector_store import get_vector_store, VectorStore


router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


# Request/Response schemas
class DocumentCreate(BaseModel):
    title: str
    content: str
    source: str
    doc_type: str
    doc_metadata: Optional[dict] = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    source: str
    doc_type: str
    content_preview: str
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5


class SearchResult(BaseModel):
    id: int
    title: str
    source: str
    doc_type: str
    content_preview: str
    

class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    sources: List[str]


def get_vector_store_dep(db: Session = Depends(get_db)) -> VectorStore:
    """Dependency to get VectorStore instance."""
    return get_vector_store(db)


@router.post("/documents", response_model=DocumentResponse)
async def add_document(
    doc: DocumentCreate,
    vector_store: VectorStore = Depends(get_vector_store_dep)
):
    """Add a new document to the knowledge base.
    
    The document will be embedded and stored for RAG retrieval.
    """
    doc_id = vector_store.add_document(
        title=doc.title,
        content=doc.content,
        source=doc.source,
        doc_type=doc.doc_type,
        doc_metadata=doc.doc_metadata
    )
    
    if doc_id is None:
        raise HTTPException(status_code=500, detail="Failed to add document")
    
    return DocumentResponse(
        id=doc_id,
        title=doc.title,
        source=doc.source,
        doc_type=doc.doc_type,
        content_preview=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
    )


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    source: str = Form(...),
    doc_type: str = Form(...),
    vector_store: VectorStore = Depends(get_vector_store_dep)
):
    """Upload a text file to the knowledge base.
    
    Supports .txt and .md files.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    allowed_extensions = {".txt", ".md", ".text"}
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    content = (await file.read()).decode("utf-8")
    
    doc_id = vector_store.add_document(
        title=title,
        content=content,
        source=source,
        doc_type=doc_type
    )
    
    return {"status": "success", "document_id": doc_id, "characters": len(content)}


@router.get("/search", response_model=List[SearchResult])
async def search_knowledge(
    query: str,
    limit: int = 5,
    vector_store: VectorStore = Depends(get_vector_store_dep)
):
    """Search the knowledge base using semantic similarity.
    
    Returns documents most relevant to the query.
    """
    documents = vector_store.search(query, limit=limit)
    
    return [
        SearchResult(
            id=doc.id,
            title=doc.title,
            source=doc.source,
            doc_type=doc.doc_type,
            content_preview=doc.content[:300] + "..." if len(doc.content) > 300 else doc.content
        )
        for doc in documents
    ]


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    limit: int = 50,
    offset: int = 0,
    vector_store: VectorStore = Depends(get_vector_store_dep)
):
    """List all documents in the knowledge base."""
    documents = vector_store.list_all(limit=limit, offset=offset)
    
    return [
        DocumentResponse(
            id=doc.id,
            title=doc.title,
            source=doc.source,
            doc_type=doc.doc_type,
            content_preview=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
        )
        for doc in documents
    ]


@router.get("/documents/{doc_id}")
async def get_document(
    doc_id: int,
    vector_store: VectorStore = Depends(get_vector_store_dep)
):
    """Get a specific document by ID."""
    doc = vector_store.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "source": doc.source,
        "doc_type": doc.doc_type,
        "created_at": doc.created_at,
        "doc_metadata": doc.doc_metadata
    }


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    vector_store: VectorStore = Depends(get_vector_store_dep)
):
    """Delete a document from the knowledge base."""
    success = vector_store.delete(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": doc_id}


@router.get("/stats", response_model=KnowledgeStatsResponse)
async def get_stats(
    vector_store: VectorStore = Depends(get_vector_store_dep)
):
    """Get knowledge base statistics."""
    total = vector_store.count()
    
    # Get unique sources
    documents = vector_store.list_all(limit=1000)
    sources = list(set(doc.source for doc in documents))
    
    return KnowledgeStatsResponse(
        total_documents=total,
        sources=sources
    )
