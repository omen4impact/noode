"""Knowledge Store for agent memory and RAG.

Provides persistent vector storage for:
- Code snippets and documentation
- Past decisions and their outcomes
- Best practices and patterns
- Research findings
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from pathlib import Path
import json

import structlog

logger = structlog.get_logger()


@dataclass
class KnowledgeEntry:
    """A piece of knowledge stored in the system."""
    
    entry_id: str
    content: str
    entry_type: str  # code, doc, decision, pattern, research
    source: str  # Where this knowledge came from
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    relevance_score: float = 1.0


@dataclass
class SearchResult:
    """Result of a knowledge search."""
    
    entry: KnowledgeEntry
    similarity: float
    context: str | None = None


class KnowledgeStore:
    """Vector-based knowledge storage and retrieval.
    
    Uses embeddings for semantic search and stores knowledge
    that can be retrieved by agents during task execution.
    
    Supports multiple backends:
    - In-memory (default, for development)
    - SQLite + FAISS (for local persistence)
    - PostgreSQL + pgvector (for production)
    """
    
    def __init__(
        self,
        storage_path: Path | None = None,
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        """Initialize the knowledge store.
        
        Args:
            storage_path: Path for persistent storage (None = in-memory)
            embedding_model: Model to use for embeddings
        """
        self.storage_path = storage_path
        self.embedding_model = embedding_model
        
        # In-memory storage
        self._entries: dict[str, KnowledgeEntry] = {}
        
        # Index for fast search (would use FAISS in production)
        self._embedding_index: list[tuple[str, list[float]]] = []
        
        # Load existing knowledge if path provided
        if storage_path and storage_path.exists():
            self._load_from_disk()
        
        logger.info("knowledge_store_initialized", storage=str(storage_path))
    
    async def add(
        self,
        content: str,
        entry_type: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeEntry:
        """Add knowledge to the store.
        
        Args:
            content: The knowledge content
            entry_type: Type of knowledge
            source: Where this came from
            metadata: Additional metadata
            
        Returns:
            Created knowledge entry
        """
        import uuid
        
        entry_id = str(uuid.uuid4())[:12]
        
        # Generate embedding
        embedding = await self._get_embedding(content)
        
        entry = KnowledgeEntry(
            entry_id=entry_id,
            content=content,
            entry_type=entry_type,
            source=source,
            embedding=embedding,
            metadata=metadata or {},
        )
        
        self._entries[entry_id] = entry
        
        if embedding:
            self._embedding_index.append((entry_id, embedding))
        
        logger.info(
            "knowledge_added",
            entry_id=entry_id,
            type=entry_type,
            source=source[:50],
        )
        
        # Persist if storage path set
        if self.storage_path:
            await self._save_to_disk()
        
        return entry
    
    async def search(
        self,
        query: str,
        entry_type: str | None = None,
        limit: int = 5,
        min_similarity: float = 0.5,
    ) -> list[SearchResult]:
        """Search for relevant knowledge.
        
        Args:
            query: Search query
            entry_type: Optional filter by type
            limit: Maximum results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of search results
        """
        if not self._entries:
            return []
        
        # Get query embedding
        query_embedding = await self._get_embedding(query)
        
        if not query_embedding:
            # Fall back to keyword search
            return self._keyword_search(query, entry_type, limit)
        
        # Calculate similarities
        results: list[tuple[str, float]] = []
        
        for entry_id, embedding in self._embedding_index:
            entry = self._entries.get(entry_id)
            
            if not entry:
                continue
            
            if entry_type and entry.entry_type != entry_type:
                continue
            
            similarity = self._cosine_similarity(query_embedding, embedding)
            
            if similarity >= min_similarity:
                results.append((entry_id, similarity))
        
        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Build search results
        search_results = []
        for entry_id, similarity in results[:limit]:
            entry = self._entries[entry_id]
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            search_results.append(SearchResult(
                entry=entry,
                similarity=similarity,
            ))
        
        logger.info(
            "knowledge_searched",
            query=query[:50],
            results=len(search_results),
        )
        
        return search_results
    
    async def get(self, entry_id: str) -> KnowledgeEntry | None:
        """Get a specific knowledge entry.
        
        Args:
            entry_id: ID of the entry
            
        Returns:
            The entry or None
        """
        entry = self._entries.get(entry_id)
        
        if entry:
            entry.access_count += 1
            entry.last_accessed = datetime.now()
        
        return entry
    
    async def update(
        self,
        entry_id: str,
        content: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeEntry | None:
        """Update a knowledge entry.
        
        Args:
            entry_id: ID of entry to update
            content: New content (optional)
            metadata: New metadata (optional)
            
        Returns:
            Updated entry or None
        """
        entry = self._entries.get(entry_id)
        
        if not entry:
            return None
        
        if content:
            entry.content = content
            entry.embedding = await self._get_embedding(content)
            
            # Update index
            self._embedding_index = [
                (eid, emb) for eid, emb in self._embedding_index
                if eid != entry_id
            ]
            if entry.embedding:
                self._embedding_index.append((entry_id, entry.embedding))
        
        if metadata:
            entry.metadata.update(metadata)
        
        if self.storage_path:
            await self._save_to_disk()
        
        return entry
    
    async def delete(self, entry_id: str) -> bool:
        """Delete a knowledge entry.
        
        Args:
            entry_id: ID of entry to delete
            
        Returns:
            True if deleted
        """
        if entry_id not in self._entries:
            return False
        
        del self._entries[entry_id]
        self._embedding_index = [
            (eid, emb) for eid, emb in self._embedding_index
            if eid != entry_id
        ]
        
        if self.storage_path:
            await self._save_to_disk()
        
        return True
    
    def get_stats(self) -> dict[str, Any]:
        """Get store statistics.
        
        Returns:
            Statistics dictionary
        """
        type_counts: dict[str, int] = {}
        for entry in self._entries.values():
            type_counts[entry.entry_type] = type_counts.get(entry.entry_type, 0) + 1
        
        return {
            "total_entries": len(self._entries),
            "indexed_entries": len(self._embedding_index),
            "by_type": type_counts,
            "storage_path": str(self.storage_path) if self.storage_path else "memory",
        }
    
    async def _get_embedding(self, text: str) -> list[float] | None:
        """Get embedding for text using LiteLLM."""
        try:
            import litellm
            
            response = await litellm.aembedding(
                model=self.embedding_model,
                input=text[:8191],  # Limit to model max
            )
            
            return response.data[0]["embedding"]
            
        except Exception as e:
            logger.warning("embedding_failed", error=str(e))
            return None
    
    def _cosine_similarity(
        self,
        vec1: list[float],
        vec2: list[float],
    ) -> float:
        """Calculate cosine similarity between vectors."""
        import math
        
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _keyword_search(
        self,
        query: str,
        entry_type: str | None,
        limit: int,
    ) -> list[SearchResult]:
        """Fallback keyword search when embeddings unavailable."""
        query_lower = query.lower()
        results = []
        
        for entry in self._entries.values():
            if entry_type and entry.entry_type != entry_type:
                continue
            
            # Simple keyword matching
            content_lower = entry.content.lower()
            if query_lower in content_lower:
                # Calculate simple relevance
                count = content_lower.count(query_lower)
                similarity = min(1.0, count * 0.2 + 0.5)
                
                results.append(SearchResult(
                    entry=entry,
                    similarity=similarity,
                ))
        
        results.sort(key=lambda x: x.similarity, reverse=True)
        return results[:limit]
    
    async def _save_to_disk(self) -> None:
        """Persist knowledge to disk."""
        if not self.storage_path:
            return
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        data = {
            entry_id: {
                "entry_id": e.entry_id,
                "content": e.content,
                "entry_type": e.entry_type,
                "source": e.source,
                "embedding": e.embedding,
                "metadata": e.metadata,
                "created_at": e.created_at.isoformat(),
                "access_count": e.access_count,
                "relevance_score": e.relevance_score,
            }
            for entry_id, e in self._entries.items()
        }
        
        (self.storage_path / "knowledge.json").write_text(
            json.dumps(data, indent=2)
        )
        
        logger.debug("knowledge_persisted", entries=len(data))
    
    def _load_from_disk(self) -> None:
        """Load knowledge from disk."""
        if not self.storage_path:
            return
        
        knowledge_file = self.storage_path / "knowledge.json"
        
        if not knowledge_file.exists():
            return
        
        data = json.loads(knowledge_file.read_text())
        
        for entry_id, e in data.items():
            entry = KnowledgeEntry(
                entry_id=e["entry_id"],
                content=e["content"],
                entry_type=e["entry_type"],
                source=e["source"],
                embedding=e.get("embedding"),
                metadata=e.get("metadata", {}),
                created_at=datetime.fromisoformat(e["created_at"]),
                access_count=e.get("access_count", 0),
                relevance_score=e.get("relevance_score", 1.0),
            )
            
            self._entries[entry_id] = entry
            
            if entry.embedding:
                self._embedding_index.append((entry_id, entry.embedding))
        
        logger.info("knowledge_loaded", entries=len(self._entries))
