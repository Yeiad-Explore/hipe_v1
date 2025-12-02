"""Reddit API client."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import praw
from praw.models import Submission, Comment
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from loguru import logger

from models.schemas import SearchResult, SourceAttribution

load_dotenv()


class RedditClient:
    """Client for Reddit API using PRAW."""

    def __init__(self):
        """Initialize Reddit API client."""
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "QA_Agent/1.0")

        if not all([self.client_id, self.client_secret]):
            logger.warning("Reddit API credentials not set. Reddit search will be disabled.")
            self.reddit = None
            return

        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )
            logger.info("Reddit API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            self.reddit = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=16),
        reraise=True,
    )
    def search_reddit(
        self,
        query: str,
        max_results: int = 20,
        time_filter: str = "month",  # all, year, month, week, day, hour
        subreddits: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Search Reddit posts and comments.

        Args:
            query: Search query
            max_results: Maximum number of results
            time_filter: Time filter (all, year, month, week, day, hour)
            subreddits: List of specific subreddits to search (None = all)

        Returns:
            List[SearchResult]: List of search results
        """
        if not self.reddit:
            logger.warning("Reddit client not available")
            return []

        try:
            results = []

            # Determine search scope
            if subreddits:
                search_scope = self.reddit.subreddit("+".join(subreddits))
            else:
                search_scope = self.reddit.subreddit("all")

            # Search submissions
            submissions = search_scope.search(
                query=query,
                time_filter=time_filter,
                limit=max_results,
                sort="relevance",
            )

            for submission in submissions:
                # Skip removed/deleted posts
                if submission.removed_by_category or submission.selftext == "[removed]":
                    continue

                # Calculate engagement
                engagement = {
                    "upvotes": submission.score,
                    "upvote_ratio": int(submission.upvote_ratio * 100),
                    "num_comments": submission.num_comments,
                    "awards": submission.total_awards_received,
                }

                # Calculate credibility based on subreddit and awards
                credibility = 0.5
                if submission.total_awards_received > 0:
                    credibility += 0.2
                if submission.upvote_ratio > 0.8:
                    credibility += 0.2
                if submission.num_comments > 50:
                    credibility += 0.1
                credibility = min(credibility, 1.0)

                # Calculate relevance based on score and engagement
                relevance = min(submission.score / 1000, 1.0)

                # Get post content
                content = submission.title
                if submission.selftext and len(submission.selftext) > 0:
                    content += f"\n\n{submission.selftext[:1000]}"  # Limit length

                source = SourceAttribution(
                    platform="reddit",
                    url=f"https://reddit.com{submission.permalink}",
                    author=f"u/{submission.author.name}" if submission.author else "[deleted]",
                    timestamp=datetime.fromtimestamp(submission.created_utc),
                    engagement=engagement,
                    credibility_score=credibility,
                )

                result = SearchResult(
                    platform="reddit",
                    content=content,
                    source=source,
                    relevance_score=relevance,
                    metadata={
                        "post_id": submission.id,
                        "subreddit": str(submission.subreddit),
                        "is_self": submission.is_self,
                        "flair": submission.link_flair_text,
                    },
                )
                results.append(result)

                # Also get top comments for context
                submission.comments.replace_more(limit=0)
                top_comments = list(submission.comments)[:3]  # Top 3 comments

                for comment in top_comments:
                    if isinstance(comment, Comment) and len(comment.body) > 50:
                        comment_engagement = {
                            "upvotes": comment.score,
                            "awards": comment.total_awards_received,
                        }

                        comment_credibility = 0.5
                        if comment.total_awards_received > 0:
                            credibility += 0.3
                        if comment.score > 100:
                            credibility += 0.2
                        comment_credibility = min(comment_credibility, 1.0)

                        comment_source = SourceAttribution(
                            platform="reddit",
                            url=f"https://reddit.com{submission.permalink}{comment.id}",
                            author=f"u/{comment.author.name}" if comment.author else "[deleted]",
                            timestamp=datetime.fromtimestamp(comment.created_utc),
                            engagement=comment_engagement,
                            credibility_score=comment_credibility,
                        )

                        comment_result = SearchResult(
                            platform="reddit",
                            content=comment.body[:1000],  # Limit length
                            source=comment_source,
                            relevance_score=min(comment.score / 500, 1.0),
                            metadata={
                                "comment_id": comment.id,
                                "parent_id": submission.id,
                                "subreddit": str(submission.subreddit),
                                "is_comment": True,
                            },
                        )
                        results.append(comment_result)

            logger.info(f"Retrieved {len(results)} results from Reddit for query: {query}")
            return results[:max_results]  # Limit to max_results

        except Exception as e:
            logger.error(f"Reddit API error: {e}")
            return []

    def get_subreddit_suggestions(self, query: str) -> List[str]:
        """
        Suggest relevant subreddits for a query.

        Args:
            query: Search query

        Returns:
            List[str]: List of relevant subreddit names
        """
        if not self.reddit:
            return []

        try:
            # Search for subreddits
            subreddits = self.reddit.subreddits.search(query, limit=5)
            names = [sub.display_name for sub in subreddits]
            logger.debug(f"Suggested subreddits for '{query}': {names}")
            return names

        except Exception as e:
            logger.error(f"Error getting subreddit suggestions: {e}")
            return []
