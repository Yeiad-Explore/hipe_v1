"""Synthesis Agent - Generates final answer from multiple sources."""
import json
from typing import Dict, Any, List
from collections import Counter
from loguru import logger

from clients.azure_openai import AzureOpenAIClient
from models.schemas import AgentState, FinalAnswer, SourceAttribution


def synthesize_answer(state: AgentState) -> Dict[str, Any]:
    """
    Synthesize final answer from top-K content.

    This agent:
    1. Aggregates information from multiple sources
    2. Identifies consensus vs conflicting viewpoints
    3. Generates comprehensive answer with citations
    4. Calculates confidence score
    5. Provides source attributions

    Args:
        state: Current agent state with top_k_content

    Returns:
        Dict with final_answer
    """
    logger.info("Synthesizing final answer")

    try:
        client = AzureOpenAIClient()

        if not state.top_k_content:
            logger.warning("No content available for synthesis")
            return {
                "final_answer": FinalAnswer(
                    answer="I couldn't find relevant information to answer your question. Please try rephrasing or checking the API credentials.",
                    confidence=0.0,
                    sources=[],
                    perspectives={},
                    consensus_level="low",
                    metadata={"error": "no_content"},
                )
            }

        # Prepare context from top-K content
        context_parts = []
        sources = []

        for idx, content in enumerate(state.top_k_content):
            source_label = f"Source {idx + 1}"
            context_parts.append(
                f"[{source_label}] ({content.source.platform} - {content.source.author})\n"
                f"{content.content}\n"
                f"Credibility: {content.source.credibility_score:.2f}, "
                f"Relevance: {content.final_score:.2f}\n"
            )
            sources.append(content.source)

        context = "\n---\n".join(context_parts)

        # System prompt for synthesis
        system_prompt = """You are an expert information synthesizer. Given multiple sources from X (Twitter) and Reddit, create a comprehensive answer.

Your response should be a JSON object:
{
  "answer": "Main comprehensive answer (2-4 paragraphs)",
  "key_points": ["bullet", "points", "of", "key", "info"],
  "perspectives": {
    "consensus": "What most sources agree on",
    "alternative": "Any conflicting or minority viewpoints",
    "expert": "Insights from high-credibility sources"
  },
  "consensus_level": "high" | "medium" | "low" | "conflicting",
  "confidence_factors": {
    "source_quality": 0.0-1.0,
    "information_consistency": 0.0-1.0,
    "recency": 0.0-1.0
  }
}

Guidelines:
- Synthesize information, don't just summarize sources
- Identify consensus and note disagreements
- Prioritize high-credibility sources
- Be objective, present different viewpoints
- If information is conflicting, acknowledge it
- Use natural language, avoid "Source 1 says..."
"""

        messages = [
            {
                "role": "user",
                "content": f"Query: {state.query}\n\nSources:\n{context}\n\nSynthesize a comprehensive answer.",
            }
        ]

        response = client.structured_output(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.5,
        )

        # Parse JSON response
        synthesis = json.loads(response)

        # Calculate overall confidence
        factors = synthesis.get("confidence_factors", {})
        confidence = (
            factors.get("source_quality", 0.7) * 0.4
            + factors.get("information_consistency", 0.7) * 0.4
            + factors.get("recency", 0.7) * 0.2
        )

        # Create FinalAnswer
        final_answer = FinalAnswer(
            answer=synthesis["answer"],
            confidence=round(confidence, 2),
            sources=sources,
            perspectives=synthesis.get("perspectives", {}),
            consensus_level=synthesis.get("consensus_level", "medium"),
            metadata={
                "num_sources": len(sources),
                "platforms": _count_platforms(sources),
                "key_points": synthesis.get("key_points", []),
                "confidence_factors": factors,
            },
        )

        logger.info(
            f"Answer synthesized - Confidence: {final_answer.confidence:.2f}, "
            f"Sources: {len(final_answer.sources)}, "
            f"Consensus: {final_answer.consensus_level}"
        )

        return {"final_answer": final_answer}

    except Exception as e:
        logger.error(f"Error in answer synthesis: {e}")
        return {
            "final_answer": FinalAnswer(
                answer="An error occurred while synthesizing the answer. Please try again.",
                confidence=0.0,
                sources=[],
                perspectives={},
                consensus_level="low",
                metadata={"error": str(e)},
            )
        }


def _count_platforms(sources: List[SourceAttribution]) -> Dict[str, int]:
    """Count sources by platform."""
    platforms = [source.platform for source in sources]
    return dict(Counter(platforms))
