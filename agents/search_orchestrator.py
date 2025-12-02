"""Search Orchestrator Agent - Decides search strategy and executes searches."""
import os
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

from clients.x_client import XClient
from clients.reddit_client import RedditClient
from models.schemas import AgentState, SearchResult


def orchestrate_search(state: AgentState) -> Dict[str, Any]:
    """
    Orchestrate parallel searches across X and Reddit.

    This agent:
    1. Determines which platforms to search based on query intent
    2. Executes searches in parallel for efficiency
    3. Applies platform-specific search strategies
    4. Returns combined results

    Args:
        state: Current agent state with query_intent

    Returns:
        Dict with x_results and reddit_results
    """
    logger.info("Orchestrating search across platforms")

    query_intent = state.query_intent
    if not query_intent:
        logger.error("No query intent available")
        return {"x_results": [], "reddit_results": []}

    max_results = int(os.getenv("MAX_SEARCH_RESULTS", "20"))

    # Initialize clients
    x_client = XClient()
    reddit_client = RedditClient()

    x_results = []
    reddit_results = []

    # Prepare search queries (use original + expanded)
    queries_to_search = [query_intent.original_query] + query_intent.expanded_queries[:2]
    main_query = query_intent.original_query

    def search_x() -> List[SearchResult]:
        """Search X (Twitter)."""
        if not query_intent.requires_x:
            logger.info("X search not required for this query")
            return []

        try:
            # For recent events, search last 3 days; otherwise 7 days
            days_back = 3 if query_intent.intent_type == "recent_events" else 7

            # Search with main query
            results = x_client.search_recent_tweets(
                query=main_query,
                max_results=max_results,
                days_back=days_back,
            )
            logger.info(f"Found {len(results)} tweets from X")
            return results

        except Exception as e:
            logger.error(f"Error searching X: {e}")
            return []

    def search_reddit() -> List[SearchResult]:
        """Search Reddit."""
        if not query_intent.requires_reddit:
            logger.info("Reddit search not required for this query")
            return []

        try:
            # Determine time filter based on intent
            time_filter = "week" if query_intent.intent_type == "recent_events" else "month"

            # Get subreddit suggestions for better targeting
            subreddits = reddit_client.get_subreddit_suggestions(main_query)

            # Search with main query
            results = reddit_client.search_reddit(
                query=main_query,
                max_results=max_results,
                time_filter=time_filter,
                subreddits=subreddits if subreddits else None,
            )
            logger.info(f"Found {len(results)} posts/comments from Reddit")
            return results

        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []

    # Execute searches in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_x = executor.submit(search_x)
        future_reddit = executor.submit(search_reddit)

        # Collect results
        for future in as_completed([future_x, future_reddit]):
            try:
                result = future.result()
                if future == future_x:
                    x_results = result
                else:
                    reddit_results = result
            except Exception as e:
                logger.error(f"Error in parallel search: {e}")

    logger.info(
        f"Search orchestration complete - X: {len(x_results)}, Reddit: {len(reddit_results)}"
    )

    return {
        "x_results": x_results,
        "reddit_results": reddit_results,
    }
