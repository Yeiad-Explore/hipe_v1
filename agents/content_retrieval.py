"""Content Retrieval Agent - Processes, embeds, and ranks content."""
import os
from typing import Dict, Any, List, Tuple
from loguru import logger

from clients.azure_openai import AzureOpenAIClient
from models.schemas import AgentState, ProcessedContent, SearchResult
from utils.embeddings import rank_by_similarity, maximal_marginal_relevance


def retrieve_and_process(state: AgentState) -> Dict[str, Any]:
    """
    Process search results with embeddings and semantic ranking.

    This agent:
    1. Combines results from all platforms
    2. Generates embeddings for query and all content
    3. Performs semantic similarity ranking
    4. Applies MMR for diversity
    5. Selects top-K most relevant content

    Args:
        state: Current agent state with search results

    Returns:
        Dict with processed_content and top_k_content
    """
    logger.info("Processing and ranking content")

    try:
        client = AzureOpenAIClient()
        top_k = int(os.getenv("TOP_K_RETRIEVAL", "10"))

        # Combine all search results
        all_results = state.x_results + state.reddit_results

        if not all_results:
            logger.warning("No search results to process")
            return {"processed_content": [], "top_k_content": []}

        logger.info(f"Processing {len(all_results)} search results")

        # Prepare texts for embedding
        query_text = state.query_intent.original_query if state.query_intent else state.query
        content_texts = [result.content for result in all_results]

        # Generate embeddings (batch for efficiency)
        all_texts = [query_text] + content_texts
        embeddings = client.get_embeddings(all_texts)

        query_embedding = embeddings[0]
        content_embeddings = embeddings[1:]

        # Create ProcessedContent objects
        processed_items = []
        for idx, (result, embedding) in enumerate(zip(all_results, content_embeddings)):
            # Calculate semantic similarity
            from utils.embeddings import cosine_similarity
            semantic_score = cosine_similarity(query_embedding, embedding)

            # Combine with platform relevance score
            # 70% semantic, 30% platform relevance
            final_score = 0.7 * semantic_score + 0.3 * result.relevance_score

            processed = ProcessedContent(
                content=result.content,
                embedding=embedding,
                source=result.source,
                relevance_score=result.relevance_score,
                semantic_score=semantic_score,
                final_score=final_score,
                chunk_id=f"{result.platform}_{idx}",
            )
            processed_items.append(processed)

        # Sort by final score
        processed_items.sort(key=lambda x: x.final_score, reverse=True)

        logger.info(f"Processed {len(processed_items)} items")

        # Apply MMR for diversity in top-K selection
        content_embeddings_with_idx = [
            (idx, item.embedding) for idx, item in enumerate(processed_items)
        ]

        # Use MMR to select diverse top-K
        mmr_results = maximal_marginal_relevance(
            query_embedding=query_embedding,
            content_embeddings=content_embeddings_with_idx,
            top_k=min(top_k, len(processed_items)),
            lambda_param=0.6,  # Balance relevance and diversity
        )

        # Get top-K items
        top_k_indices = [idx for idx, score in mmr_results]
        top_k_content = [processed_items[idx] for idx in top_k_indices]

        logger.info(f"Selected top {len(top_k_content)} diverse items for synthesis")

        return {
            "processed_content": processed_items,
            "top_k_content": top_k_content,
        }

    except Exception as e:
        logger.error(f"Error in content retrieval: {e}")
        return {"processed_content": [], "top_k_content": []}
