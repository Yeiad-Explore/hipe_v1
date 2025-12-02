"""Vector store for caching queries and results."""
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import chromadb
from chromadb.config import Settings
from loguru import logger


class VectorCache:
    """
    Vector database cache for query results.

    Uses ChromaDB to cache:
    - Query embeddings
    - Search results
    - Final answers

    This reduces API calls and improves response time for similar queries.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        """
        Initialize vector cache.

        Args:
            persist_dir: Directory to persist the database
        """
        if not persist_dir:
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

        self.persist_dir = persist_dir
        self.ttl_hours = int(os.getenv("CACHE_TTL_HOURS", "24"))

        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="qa_cache",
                metadata={"description": "Cached Q&A results"},
            )

            logger.info(f"Vector cache initialized at {persist_dir}")

        except Exception as e:
            logger.error(f"Failed to initialize vector cache: {e}")
            self.client = None
            self.collection = None

    def get_similar_query(
        self,
        query_embedding: List[float],
        similarity_threshold: float = 0.9,
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a similar query exists in cache.

        Args:
            query_embedding: Embedding of the query
            similarity_threshold: Minimum similarity to consider a match

        Returns:
            Cached result if found, None otherwise
        """
        if not self.collection:
            return None

        try:
            # Query for similar embeddings
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1,
            )

            if not results["ids"] or not results["ids"][0]:
                return None

            # Check if similar enough
            distance = results["distances"][0][0]
            # ChromaDB uses L2 distance; convert to similarity
            similarity = 1 / (1 + distance)

            if similarity < similarity_threshold:
                logger.debug(f"Found cached query but similarity too low: {similarity:.3f}")
                return None

            # Check if expired
            metadata = results["metadatas"][0][0]
            cached_at = datetime.fromisoformat(metadata["cached_at"])
            age_hours = (datetime.now() - cached_at).total_seconds() / 3600

            if age_hours > self.ttl_hours:
                logger.debug(f"Cached query expired (age: {age_hours:.1f}h)")
                return None

            # Return cached result
            cached_result = {
                "answer": metadata["answer"],
                "confidence": float(metadata["confidence"]),
                "cached_at": cached_at.isoformat(),
                "age_hours": round(age_hours, 1),
            }

            logger.info(f"Cache hit! Returning cached result (age: {age_hours:.1f}h)")
            return cached_result

        except Exception as e:
            logger.error(f"Error querying cache: {e}")
            return None

    def cache_result(
        self,
        query: str,
        query_embedding: List[float],
        answer: str,
        confidence: float,
        metadata: Optional[Dict] = None,
    ):
        """
        Cache a query result.

        Args:
            query: Original query text
            query_embedding: Query embedding vector
            answer: Generated answer
            confidence: Confidence score
            metadata: Additional metadata
        """
        if not self.collection:
            return

        try:
            cache_metadata = {
                "query": query,
                "answer": answer,
                "confidence": str(confidence),
                "cached_at": datetime.now().isoformat(),
            }

            if metadata:
                cache_metadata.update({k: str(v) for k, v in metadata.items()})

            # Add to collection
            self.collection.add(
                ids=[f"query_{datetime.now().timestamp()}"],
                embeddings=[query_embedding],
                metadatas=[cache_metadata],
            )

            logger.debug("Result cached successfully")

        except Exception as e:
            logger.error(f"Error caching result: {e}")

    def clear_expired(self):
        """Clear expired cache entries."""
        if not self.collection:
            return

        try:
            # Get all items
            all_items = self.collection.get()

            expired_ids = []
            cutoff_time = datetime.now() - timedelta(hours=self.ttl_hours)

            for idx, metadata in enumerate(all_items["metadatas"]):
                cached_at = datetime.fromisoformat(metadata["cached_at"])
                if cached_at < cutoff_time:
                    expired_ids.append(all_items["ids"][idx])

            if expired_ids:
                self.collection.delete(ids=expired_ids)
                logger.info(f"Cleared {len(expired_ids)} expired cache entries")

        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
