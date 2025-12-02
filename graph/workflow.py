"""LangGraph workflow for Q&A agent."""
import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from loguru import logger

from models.schemas import AgentState
from agents import (
    analyze_query,
    orchestrate_search,
    retrieve_and_process,
    synthesize_answer,
)


def create_qa_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for Q&A agent.

    Workflow:
    1. Query Analyst: Understand intent and expand query
    2. Search Orchestrator: Parallel search X and Reddit
    3. Content Retrieval: Embed, rank, and select top-K
    4. Synthesis: Generate final answer with sources

    Returns:
        StateGraph: Compiled workflow
    """
    # Create state graph with AgentState
    workflow = StateGraph(AgentState)

    # Add nodes (agents)
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("orchestrate_search", orchestrate_search)
    workflow.add_node("retrieve_and_process", retrieve_and_process)
    workflow.add_node("synthesize_answer", synthesize_answer)

    # Define edges (workflow flow)
    workflow.set_entry_point("analyze_query")
    workflow.add_edge("analyze_query", "orchestrate_search")
    workflow.add_edge("orchestrate_search", "retrieve_and_process")
    workflow.add_edge("retrieve_and_process", "synthesize_answer")
    workflow.add_edge("synthesize_answer", END)

    # Compile the graph
    compiled_workflow = workflow.compile()

    logger.info("Q&A workflow created and compiled")
    return compiled_workflow


class QAAgent:
    """
    Main Q&A Agent class.

    High-level interface for querying the multi-agent system.
    """

    def __init__(self):
        """Initialize the Q&A agent."""
        self.workflow = create_qa_workflow()
        logger.info("QAAgent initialized")

    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a query through the multi-agent workflow.

        Args:
            question: User's question

        Returns:
            Dict containing:
                - answer: The synthesized answer
                - confidence: Confidence score (0-1)
                - sources: List of source attributions
                - perspectives: Different viewpoints
                - consensus_level: Level of agreement
                - metadata: Additional info
                - processing_time: Time taken
        """
        logger.info(f"Processing query: {question}")
        start_time = time.time()

        try:
            # Create initial state
            initial_state = AgentState(query=question)

            # Run workflow
            final_state = self.workflow.invoke(initial_state)

            # Extract final answer
            final_answer = final_state.get("final_answer")

            if not final_answer:
                logger.error("No final answer generated")
                return {
                    "answer": "Unable to generate answer.",
                    "confidence": 0.0,
                    "sources": [],
                    "perspectives": {},
                    "consensus_level": "low",
                    "metadata": {"error": "no_final_answer"},
                    "processing_time": time.time() - start_time,
                }

            # Format response
            processing_time = time.time() - start_time

            response = {
                "answer": final_answer.answer,
                "confidence": final_answer.confidence,
                "sources": [
                    {
                        "platform": source.platform,
                        "url": source.url,
                        "author": source.author,
                        "timestamp": source.timestamp.isoformat(),
                        "engagement": source.engagement,
                        "credibility_score": source.credibility_score,
                    }
                    for source in final_answer.sources
                ],
                "perspectives": final_answer.perspectives,
                "consensus_level": final_answer.consensus_level,
                "metadata": final_answer.metadata,
                "processing_time": round(processing_time, 2),
            }

            logger.info(
                f"Query processed successfully in {processing_time:.2f}s - "
                f"Confidence: {final_answer.confidence:.2f}"
            )

            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "perspectives": {},
                "consensus_level": "low",
                "metadata": {"error": str(e)},
                "processing_time": time.time() - start_time,
            }

    def stream_query(self, question: str):
        """
        Stream the query processing (future enhancement).

        Args:
            question: User's question

        Yields:
            Updates from each agent step
        """
        logger.info(f"Streaming query: {question}")
        initial_state = AgentState(query=question)

        for step in self.workflow.stream(initial_state):
            yield step
