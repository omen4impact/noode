"""Knowledge Store with Vector Database (Qdrant) for RAG.

This module provides:
- Document storage with vector embeddings
- Semantic search using vector similarity
- RAG (Retrieval Augmented Generation) support
- Code and documentation indexing
"""

import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
import uuid
import math

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Warning: qdrant-client not installed. Knowledge Store will use fallback.")

from noode.knowledge.embeddings import EmbeddingService

logger = structlog.get_logger()


class Document:
    """Represents a document in the knowledge store."""
    
    def __init__(
        self,
        content: str,
        doc_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ):
        self.id = doc_id or str(uuid.uuid4())
        self.content = content
        self.doc_type = doc_type  # text, code, markdown, etc.
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "doc_type": self.doc_type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "has_embedding": self.embedding is not None,
        }


class KnowledgeStore:
    """Vector-based knowledge store using Qdrant."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "noode_knowledge",
        embedding_model: Optional[str] = None,
    ):
        """Initialize knowledge store.
        
        Args:
            host: Qdrant host
            port: Qdrant port
            collection_name: Name of the collection
            embedding_model: Name of the embedding model to use
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService(embedding_model)
        self._client: Optional[QdrantClient] = None
        
        if QDRANT_AVAILABLE:
            try:
                self._client = QdrantClient(host=host, port=port)
                self._ensure_collection()
                logger.info("knowledge_store_initialized", 
                          host=host, port=port, collection=collection_name)
            except Exception as e:
                logger.error("failed_to_connect_to_qdrant", error=str(e))
                self._client = None
        else:
            logger.warning("qdrant_not_available_using_memory_store")
            self._memory_store: Dict[str, Document] = {}
    
    def _ensure_collection(self):
        """Ensure the collection exists with proper configuration."""
        if not self._client:
            return
        
        try:
            # Check if collection exists
            collections = self._client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_service.embedding_dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("created_collection", collection=self.collection_name)
            else:
                logger.info("collection_exists", collection=self.collection_name)
                
        except Exception as e:
            logger.error("failed_to_ensure_collection", error=str(e))
            raise
    
    def add_document(self, document: Document) -> str:
        """Add a document to the knowledge store.
        
        Args:
            document: Document to add
            
        Returns:
            Document ID
        """
        # Generate embedding
        document.embedding = self.embedding_service.embed(document.content)
        
        if self._client:
            # Store in Qdrant
            try:
                self._client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        PointStruct(
                            id=document.id,
                            vector=document.embedding,
                            payload=document.to_dict(),
                        )
                    ],
                )
                logger.info("document_added_to_qdrant", doc_id=document.id)
            except Exception as e:
                logger.error("failed_to_add_to_qdrant", error=str(e))
                raise
        else:
            # Store in memory
            self._memory_store[document.id] = document
            logger.info("document_added_to_memory", doc_id=document.id)
        
        return document.id
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_type: Optional[str] = None,
    ) -> List[Document]:
        """Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            doc_type: Filter by document type
            
        Returns:
            List of matching documents
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed(query)
        
        if self._client:
            # Search in Qdrant
            try:
                filter_condition = None
                if doc_type:
                    filter_condition = {
                        "must": [
                            {"key": "doc_type", "match": {"value": doc_type}}
                        ]
                    }
                
                results = self._client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k,
                    query_filter=filter_condition,
                )
                
                documents = []
                for result in results:
                    doc = Document(
                        content=result.payload.get("content", ""),
                        doc_type=result.payload.get("doc_type", "text"),
                        metadata=result.payload.get("metadata", {}),
                        doc_id=result.id,
                    )
                    doc.embedding = result.vector
                    documents.append(doc)
                
                logger.info("search_completed", 
                          query_length=len(query), 
                          results=len(documents))
                return documents
                
            except Exception as e:
                logger.error("search_failed", error=str(e))
                return []
        else:
            # Search in memory (simple cosine similarity using pure Python)
            results = []
            for doc in self._memory_store.values():
                if doc_type and doc.doc_type != doc_type:
                    continue
                
                if doc.embedding:
                    # Calculate cosine similarity manually
                    doc_emb = doc.embedding
                    query_emb = query_embedding
                    
                    # Dot product
                    dot_product = sum(a * b for a, b in zip(doc_emb, query_emb))
                    
                    # Norms
                    norm_doc = math.sqrt(sum(x * x for x in doc_emb))
                    norm_query = math.sqrt(sum(x * x for x in query_emb))
                    
                    if norm_doc > 0 and norm_query > 0:
                        similarity = dot_product / (norm_doc * norm_query)
                        results.append((similarity, doc))
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x[0], reverse=True)
            return [doc for _, doc in results[:top_k]]
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the knowledge store.
        
        Args:
            doc_id: ID of document to delete
            
        Returns:
            True if deleted, False otherwise
        """
        if self._client:
            try:
                self._client.delete(
                    collection_name=self.collection_name,
                    points_selector=[doc_id],
                )
                logger.info("document_deleted_from_qdrant", doc_id=doc_id)
                return True
            except Exception as e:
                logger.error("failed_to_delete_from_qdrant", error=str(e))
                return False
        else:
            if doc_id in self._memory_store:
                del self._memory_store[doc_id]
                logger.info("document_deleted_from_memory", doc_id=doc_id)
                return True
            return False
    
    def get_stats(self) -> dict:
        """Get statistics about the knowledge store.
        
        Returns:
            Dictionary with statistics
        """
        if self._client:
            try:
                collection_info = self._client.get_collection(self.collection_name)
                return {
                    "total_documents": collection_info.points_count,
                    "embedding_dimension": self._embedding_dim,
                    "collection_name": self.collection_name,
                    "storage_type": "qdrant",
                }
            except Exception as e:
                logger.error("failed_to_get_stats", error=str(e))
                return {
                    "total_documents": 0,
                    "error": str(e),
                }
        else:
            # Memory store stats
            doc_types = {}
            for doc in self._memory_store.values():
                doc_type = doc.doc_type
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            return {
                "total_documents": len(self._memory_store),
                "embedding_dimension": self._embedding_dim,
                "document_types": doc_types,
                "storage_type": "memory",
            }


# RAG (Retrieval Augmented Generation) Helper
class RAGService:
    """Service for RAG (Retrieval Augmented Generation)."""
    
    def __init__(self, knowledge_store: KnowledgeStore):
        """Initialize RAG service.
        
        Args:
            knowledge_store: Knowledge store to use for retrieval
        """
        self.knowledge_store = knowledge_store
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        doc_type: Optional[str] = None,
    ) -> str:
        """Retrieve relevant context for a query.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            doc_type: Filter by document type
            
        Returns:
            Concatenated context string
        """
        documents = self.knowledge_store.search(query, top_k, doc_type)
        
        if not documents:
            return ""
        
        # Format context
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Document {i} [{doc.doc_type}]:\n{doc.content}\n")
        
        return "\n".join(context_parts)
    
    def augment_prompt(
        self,
        user_query: str,
        system_prompt: str = "",
        top_k: int = 5,
    ) -> str:
        """Create an augmented prompt with retrieved context.
        
        Args:
            user_query: Original user query
            system_prompt: System prompt to include
            top_k: Number of documents to retrieve
            
        Returns:
            Augmented prompt string
        """
        context = self.retrieve_context(user_query, top_k)
        
        augmented = f"""{system_prompt}

Use the following context to answer the question:

{context}

Question: {user_query}

Answer:"""
        
        return augmented
