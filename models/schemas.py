"""Pydantic models for the Q&A Agent."""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class QueryIntent(BaseModel):
    """Analyzed query intent and metadata."""
    original_query: str
    intent_type: Literal["factual", "opinion", "recent_events", "how_to", "comparison"]
    entities: List[str] = Field(default_factory=list)
    expanded_queries: List[str] = Field(default_factory=list)
    temporal_context: Optional[str] = None
    requires_x: bool = True
    requires_reddit: bool = True
    confidence: float = Field(ge=0.0, le=1.0)


class SourceAttribution(BaseModel):
    """Source attribution for content."""
    platform: Literal["x", "reddit"]
    url: str
    author: str
    timestamp: datetime
    engagement: Dict[str, int] = Field(default_factory=dict)  # likes, retweets, upvotes, etc.
    credibility_score: float = Field(ge=0.0, le=1.0, default=0.5)


class SearchResult(BaseModel):
    """Raw search result from a platform."""
    platform: Literal["x", "reddit"]
    content: str
    source: SourceAttribution
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.0)
    metadata: Dict = Field(default_factory=dict)


class ProcessedContent(BaseModel):
    """Processed and embedded content."""
    content: str
    embedding: Optional[List[float]] = None
    source: SourceAttribution
    relevance_score: float = Field(ge=0.0, le=1.0)
    semantic_score: float = Field(ge=0.0, le=1.0, default=0.0)
    final_score: float = Field(ge=0.0, le=1.0, default=0.0)
    chunk_id: Optional[str] = None


class FinalAnswer(BaseModel):
    """Final synthesized answer."""
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[SourceAttribution]
    perspectives: Dict[str, str] = Field(default_factory=dict)
    consensus_level: Literal["high", "medium", "low", "conflicting"]
    metadata: Dict = Field(default_factory=dict)


class AgentState(BaseModel):
    """State passed between agents in LangGraph."""
    # Input
    query: str

    # Query Analysis
    query_intent: Optional[QueryIntent] = None

    # Search Results
    x_results: List[SearchResult] = Field(default_factory=list)
    reddit_results: List[SearchResult] = Field(default_factory=list)

    # Processed Content
    processed_content: List[ProcessedContent] = Field(default_factory=list)
    top_k_content: List[ProcessedContent] = Field(default_factory=list)

    # Final Answer
    final_answer: Optional[FinalAnswer] = None

    # Metadata
    error: Optional[str] = None
    processing_time: float = 0.0

    class Config:
        arbitrary_types_allowed = True
