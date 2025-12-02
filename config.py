"""Configuration management for the Q&A Agent."""
import os
from typing import Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class AzureOpenAIConfig(BaseModel):
    """Azure OpenAI configuration."""
    api_key: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    endpoint: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    api_version: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"))
    chat_deployment: str = Field(default_factory=lambda: os.getenv("CHAT_MODEL_DEPLOYMENT", "chat-heavy"))
    embedding_deployment: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL_DEPLOYMENT", "embed-large"))


class XConfig(BaseModel):
    """X (Twitter) API configuration."""
    api_key: str = Field(default_factory=lambda: os.getenv("X_API_KEY", ""))
    api_secret: str = Field(default_factory=lambda: os.getenv("X_API_SECRET", ""))
    access_token: str = Field(default_factory=lambda: os.getenv("X_ACCESS_TOKEN", ""))
    access_token_secret: str = Field(default_factory=lambda: os.getenv("X_ACCESS_TOKEN_SECRET", ""))
    bearer_token: str = Field(default_factory=lambda: os.getenv("X_BEARER_TOKEN", ""))

    @property
    def is_configured(self) -> bool:
        """Check if X API is configured."""
        return bool(self.bearer_token)


class RedditConfig(BaseModel):
    """Reddit configuration (Public JSON API - no API keys needed)."""
    user_agent: str = Field(default_factory=lambda: os.getenv("REDDIT_USER_AGENT", "QA_Agent/1.0"))

    @property
    def is_configured(self) -> bool:
        """Check if Reddit is configured (always True for public API)."""
        return True  # Public JSON API doesn't require authentication


class AgentConfig(BaseModel):
    """Agent configuration."""
    max_search_results: int = Field(default_factory=lambda: int(os.getenv("MAX_SEARCH_RESULTS", "20")))
    top_k_retrieval: int = Field(default_factory=lambda: int(os.getenv("TOP_K_RETRIEVAL", "10")))
    confidence_threshold: float = Field(default_factory=lambda: float(os.getenv("CONFIDENCE_THRESHOLD", "0.6")))
    cache_ttl_hours: int = Field(default_factory=lambda: int(os.getenv("CACHE_TTL_HOURS", "24")))
    chroma_persist_dir: str = Field(default_factory=lambda: os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"))


class Config(BaseModel):
    """Master configuration."""
    azure_openai: AzureOpenAIConfig = Field(default_factory=AzureOpenAIConfig)
    x: XConfig = Field(default_factory=XConfig)
    reddit: RedditConfig = Field(default_factory=RedditConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)

    def validate_required(self) -> Dict[str, bool]:
        """
        Validate required configurations.

        Returns:
            Dict with validation status
        """
        status = {
            "azure_openai": bool(
                self.azure_openai.api_key
                and self.azure_openai.endpoint
                and self.azure_openai.chat_deployment
                and self.azure_openai.embedding_deployment
            ),
            "x_api": self.x.is_configured,
            "reddit_api": self.reddit.is_configured,
        }
        return status

    def get_summary(self) -> str:
        """
        Get configuration summary.

        Returns:
            str: Human-readable summary
        """
        status = self.validate_required()

        summary = "Configuration Status:\n"
        summary += f"  ✓ Azure OpenAI: {'Configured' if status['azure_openai'] else 'Missing'}\n"
        summary += f"  {'✓' if status['x_api'] else '✗'} X API: {'Configured' if status['x_api'] else 'Not configured (optional)'}\n"
        summary += f"  ✓ Reddit (JSON API): Always available (no API keys needed)\n"
        summary += f"\nAgent Settings:\n"
        summary += f"  Max Search Results: {self.agent.max_search_results}\n"
        summary += f"  Top-K Retrieval: {self.agent.top_k_retrieval}\n"
        summary += f"  Confidence Threshold: {self.agent.confidence_threshold}\n"
        summary += f"  Cache TTL: {self.agent.cache_ttl_hours}h\n"

        return summary


# Global config instance
config = Config()


if __name__ == "__main__":
    # Test configuration
    print(config.get_summary())
    print("\nValidation:", config.validate_required())
