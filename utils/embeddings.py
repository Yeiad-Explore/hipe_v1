"""Embedding utilities for semantic search."""
import numpy as np
from typing import List, Tuple
from loguru import logger


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        float: Cosine similarity score (0-1)
    """
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)

    dot_product = np.dot(vec1_np, vec2_np)
    norm_product = np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)

    if norm_product == 0:
        return 0.0

    return float(dot_product / norm_product)


def rank_by_similarity(
    query_embedding: List[float],
    content_embeddings: List[Tuple[int, List[float]]],
    top_k: int = 10,
) -> List[Tuple[int, float]]:
    """
    Rank content by semantic similarity to query.

    Args:
        query_embedding: Query embedding vector
        content_embeddings: List of (index, embedding) tuples
        top_k: Number of top results to return

    Returns:
        List[Tuple[int, float]]: List of (index, similarity_score) sorted by score
    """
    similarities = []
    for idx, embedding in content_embeddings:
        score = cosine_similarity(query_embedding, embedding)
        similarities.append((idx, score))

    # Sort by score descending
    similarities.sort(key=lambda x: x[1], reverse=True)
    logger.debug(f"Ranked {len(similarities)} items by similarity")

    return similarities[:top_k]


def maximal_marginal_relevance(
    query_embedding: List[float],
    content_embeddings: List[Tuple[int, List[float]]],
    top_k: int = 10,
    lambda_param: float = 0.5,
) -> List[Tuple[int, float]]:
    """
    Apply Maximal Marginal Relevance for diversity.

    MMR balances relevance to query with diversity in results.

    Args:
        query_embedding: Query embedding vector
        content_embeddings: List of (index, embedding) tuples
        top_k: Number of results to return
        lambda_param: Balance between relevance (1.0) and diversity (0.0)

    Returns:
        List[Tuple[int, float]]: List of (index, mmr_score) with diversity
    """
    if not content_embeddings:
        return []

    selected = []
    remaining = list(content_embeddings)

    # Calculate initial relevance scores
    relevance_scores = {
        idx: cosine_similarity(query_embedding, emb)
        for idx, emb in content_embeddings
    }

    # Select first item (highest relevance)
    first_idx = max(remaining, key=lambda x: relevance_scores[x[0]])[0]
    first_item = next(item for item in remaining if item[0] == first_idx)
    selected.append((first_idx, relevance_scores[first_idx]))
    remaining.remove(first_item)

    # Iteratively select remaining items
    while len(selected) < top_k and remaining:
        mmr_scores = {}

        for idx, emb in remaining:
            # Relevance to query
            relevance = relevance_scores[idx]

            # Maximum similarity to already selected items
            max_sim = max(
                cosine_similarity(emb, sel_emb)
                for sel_idx, sel_emb in content_embeddings
                if sel_idx in [s[0] for s in selected]
            )

            # MMR score
            mmr = lambda_param * relevance - (1 - lambda_param) * max_sim
            mmr_scores[idx] = mmr

        # Select item with highest MMR score
        next_idx = max(mmr_scores, key=mmr_scores.get)
        next_item = next(item for item in remaining if item[0] == next_idx)
        selected.append((next_idx, mmr_scores[next_idx]))
        remaining.remove(next_item)

    logger.debug(f"Applied MMR, selected {len(selected)} diverse items")
    return selected
