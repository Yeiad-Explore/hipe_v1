"""X (Twitter) API client."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import tweepy
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from loguru import logger

from models.schemas import SearchResult, SourceAttribution

load_dotenv()


class XClient:
    """Client for X (Twitter) API v2."""

    def __init__(self):
        """Initialize X API client."""
        self.bearer_token = os.getenv("X_BEARER_TOKEN")

        if not self.bearer_token:
            logger.warning("X_BEARER_TOKEN not set. X search will be disabled.")
            self.client = None
            return

        try:
            self.client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)
            logger.info("X API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize X client: {e}")
            self.client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=16),
        reraise=True,
    )
    def search_recent_tweets(
        self,
        query: str,
        max_results: int = 20,
        days_back: int = 7,
    ) -> List[SearchResult]:
        """
        Search recent tweets.

        Args:
            query: Search query
            max_results: Maximum number of tweets to retrieve
            days_back: How many days back to search

        Returns:
            List[SearchResult]: List of search results
        """
        if not self.client:
            logger.warning("X client not available")
            return []

        try:
            # Calculate start time
            start_time = datetime.utcnow() - timedelta(days=days_back)

            # Build query with filters for quality
            enhanced_query = f"{query} -is:retweet lang:en"

            # Search tweets with expansions and fields
            response = self.client.search_recent_tweets(
                query=enhanced_query,
                max_results=min(max_results, 100),  # API limit
                start_time=start_time,
                tweet_fields=["created_at", "public_metrics", "author_id", "conversation_id"],
                user_fields=["username", "verified", "public_metrics"],
                expansions=["author_id"],
            )

            if not response.data:
                logger.info(f"No tweets found for query: {query}")
                return []

            # Build user map
            users = {user.id: user for user in response.includes.get("users", [])}

            results = []
            for tweet in response.data:
                user = users.get(tweet.author_id)
                if not user:
                    continue

                # Calculate engagement score
                metrics = tweet.public_metrics
                engagement = {
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0),
                }
                total_engagement = sum(engagement.values())

                # Calculate credibility score based on verification and follower count
                credibility = 0.5
                if user.verified:
                    credibility += 0.3
                follower_count = user.public_metrics.get("followers_count", 0)
                if follower_count > 10000:
                    credibility += 0.2
                elif follower_count > 1000:
                    credibility += 0.1
                credibility = min(credibility, 1.0)

                # Calculate relevance score (engagement-based)
                relevance = min(total_engagement / 100, 1.0)

                source = SourceAttribution(
                    platform="x",
                    url=f"https://twitter.com/{user.username}/status/{tweet.id}",
                    author=f"@{user.username}",
                    timestamp=tweet.created_at,
                    engagement=engagement,
                    credibility_score=credibility,
                )

                result = SearchResult(
                    platform="x",
                    content=tweet.text,
                    source=source,
                    relevance_score=relevance,
                    metadata={
                        "tweet_id": str(tweet.id),
                        "conversation_id": str(tweet.conversation_id),
                        "verified": user.verified,
                    },
                )
                results.append(result)

            logger.info(f"Retrieved {len(results)} tweets for query: {query}")
            return results

        except tweepy.errors.TweepyException as e:
            logger.error(f"X API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in X search: {e}")
            return []

    def get_tweet_thread(self, conversation_id: str) -> List[str]:
        """
        Get full thread for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List[str]: List of tweets in thread
        """
        if not self.client:
            return []

        try:
            response = self.client.search_recent_tweets(
                query=f"conversation_id:{conversation_id}",
                max_results=100,
                tweet_fields=["created_at"],
            )

            if not response.data:
                return []

            # Sort by timestamp
            tweets = sorted(response.data, key=lambda t: t.created_at)
            return [tweet.text for tweet in tweets]

        except Exception as e:
            logger.error(f"Error fetching thread: {e}")
            return []
