"""Knowledge management module for Noode.

This module provides vector-based storage and retrieval for:
- Documents and text
- Code snippets
- Best practices
- Project history

Uses Qdrant for vector storage and sentence-transformers for embeddings.
"""

from noode.knowledge.embeddings import EmbeddingService, embed_text
from noode.knowledge.store import KnowledgeStore, Document, RAGService

__all__ = [
    "EmbeddingService",
    "embed_text",
    "KnowledgeStore",
    "Document",
    "RAGService",
]
