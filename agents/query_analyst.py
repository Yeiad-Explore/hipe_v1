"""Query Analyst Agent - Understands intent and expands queries."""
import json
from typing import Dict, Any
from loguru import logger

from clients.azure_openai import AzureOpenAIClient
from models.schemas import AgentState, QueryIntent


def analyze_query(state: AgentState) -> Dict[str, Any]:
    """
    Analyze query to understand intent, extract entities, and expand.

    This agent:
    1. Classifies query intent (factual, opinion, recent_events, how_to, comparison)
    2. Extracts named entities and key topics
    3. Generates expanded query variations for better search coverage
    4. Determines which platforms to search

    Args:
        state: Current agent state with query

    Returns:
        Dict with updated query_intent
    """
    logger.info(f"Analyzing query: {state.query}")

    try:
        client = AzureOpenAIClient()

        # System prompt for query analysis
        system_prompt = """You are a query analysis expert. Analyze the user's query and return a JSON object with:

{
  "intent_type": "factual" | "opinion" | "recent_events" | "how_to" | "comparison",
  "entities": ["list", "of", "key", "entities"],
  "expanded_queries": ["3-5 semantic variations of the query"],
  "temporal_context": "temporal info like 'latest', '2024', or null",
  "requires_x": true/false (use X for real-time info, breaking news, trends),
  "requires_reddit": true/false (use Reddit for detailed discussions, how-tos, opinions),
  "confidence": 0.0-1.0
}

Examples:
- "What are people saying about the new iPhone?" -> intent: opinion, requires both platforms
- "How do I fix a memory leak in Python?" -> intent: how_to, requires Reddit primarily
- "What's happening with the stock market today?" -> intent: recent_events, requires X primarily
"""

        messages = [
            {"role": "user", "content": f"Query: {state.query}"}
        ]

        response = client.structured_output(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,
        )

        # Parse JSON response
        analysis = json.loads(response)

        # Create QueryIntent object
        query_intent = QueryIntent(
            original_query=state.query,
            intent_type=analysis["intent_type"],
            entities=analysis.get("entities", []),
            expanded_queries=analysis.get("expanded_queries", []),
            temporal_context=analysis.get("temporal_context"),
            requires_x=analysis.get("requires_x", True),
            requires_reddit=analysis.get("requires_reddit", True),
            confidence=analysis.get("confidence", 0.8),
        )

        logger.info(
            f"Query analysis complete - Intent: {query_intent.intent_type}, "
            f"Entities: {query_intent.entities}, "
            f"Platforms: X={query_intent.requires_x}, Reddit={query_intent.requires_reddit}"
        )

        return {"query_intent": query_intent}

    except Exception as e:
        logger.error(f"Error in query analysis: {e}")
        # Fallback to default intent
        fallback_intent = QueryIntent(
            original_query=state.query,
            intent_type="factual",
            entities=[],
            expanded_queries=[state.query],
            temporal_context=None,
            requires_x=True,
            requires_reddit=True,
            confidence=0.5,
        )
        return {"query_intent": fallback_intent}
