"""Embedding service for vectorizing text and code.

This module provides functionality to convert text into vector embeddings
using sentence-transformers models. These embeddings are used for
semantic search and RAG (Retrieval Augmented Generation).
"""

import structlog
from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Using fallback embeddings.")

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating text embeddings."""
    
    # Default model - good balance of quality and speed
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    
    # Alternative models for different use cases
    MODELS = {
        "fast": "all-MiniLM-L6-v2",  # Fast, good quality
        "accurate": "all-mpnet-base-v2",  # Slower, better quality
        "code": "microsoft/codebert-base",  # For code embeddings
        "multilingual": "paraphrase-multilingual-MiniLM-L12-v2",  # Multi-language
    }
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       If None, uses the default model.
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model = None
        self._embedding_dim = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info("loading_embedding_model", model=self.model_name)
                self._model = SentenceTransformer(self.model_name)
                self._embedding_dim = self._model.get_sentence_embedding_dimension()
                logger.info("embedding_model_loaded", 
                          model=self.model_name, 
                          dimension=self._embedding_dim)
            except Exception as e:
                logger.error("failed_to_load_embedding_model", error=str(e))
                self._model = None
        else:
            logger.warning("sentence_transformers_not_available")
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * (self._embedding_dim or 384)
        
        if self._model is not None:
            try:
                embedding = self._model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error("embedding_failed", error=str(e))
                return self._fallback_embed(text)
        else:
            return self._fallback_embed(text)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self._model is not None:
            try:
                # Filter out empty texts
                valid_texts = [t for t in texts if t and t.strip()]
                if not valid_texts:
                    return [[0.0] * self._embedding_dim] * len(texts)
                
                embeddings = self._model.encode(
                    valid_texts, 
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                
                # Convert to list of lists
                return [emb.tolist() for emb in embeddings]
                
            except Exception as e:
                logger.error("batch_embedding_failed", error=str(e))
                # Fall back to individual embeddings
                return [self.embed(text) for text in texts]
        else:
            return [self.embed(text) for text in texts]
    
    def _fallback_embed(self, text: str) -> List[float]:
        """Fallback embedding when sentence-transformers is not available.
        
        Uses a simple hash-based approach - not semantically meaningful
        but provides consistent vectors for testing.
        
        Args:
            text: Text to create fallback embedding for
            
        Returns:
            List of floats (384 dimensions by default)
        """
        import hashlib
        
        # Create a deterministic hash-based embedding
        dim = 384
        hash_val = hashlib.md5(text.encode()).hexdigest()
        
        # Generate pseudo-random but deterministic floats
        embedding = []
        for i in range(dim):
            # Use different parts of hash
            idx = (i * 2) % len(hash_val)
            val = int(hash_val[idx:idx+2], 16) / 255.0
            # Center around 0
            val = (val - 0.5) * 2
            embedding.append(val)
        
        return embedding
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        emb1 = np.array(self.embed(text1))
        emb2 = np.array(self.embed(text2))
        
        # Calculate cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self._embedding_dim or 384
    
    @property
    def is_available(self) -> bool:
        """Check if the embedding service is available."""
        return self._model is not None


# Convenience function for quick embedding
def embed_text(text: str, model_name: Optional[str] = None) -> List[float]:
    """Quick function to embed text without creating a service instance.
    
    Args:
        text: Text to embed
        model_name: Optional model name
        
    Returns:
        Embedding vector
    """
    service = EmbeddingService(model_name)
    return service.embed(text)
