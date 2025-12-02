"""Reddit scraper client using YARS."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from yars import search, get_post
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from loguru import logger

from models.schemas import SearchResult, SourceAttribution

load_dotenv()


class RedditClient:
    """Client for Reddit using YARS (Yet Another Reddit Scraper)."""

    def __init__(self):
        """Initialize Reddit scraper client."""
        # YARS doesn't require authentication!
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "QA_Agent/1.0")
        logger.info("Reddit YARS client initialized (no API keys needed)")

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
        Search Reddit posts and comments using YARS.

        Args:
            query: Search query
            max_results: Maximum number of results
            time_filter: Time filter (all, year, month, week, day, hour)
            subreddits: List of specific subreddits to search (None = all)

        Returns:
            List[SearchResult]: List of search results
        """
        try:
            results = []

            # Determine search scope
            if subreddits:
                subreddit_query = "+".join(subreddits)
            else:
                subreddit_query = "all"

            # Search using YARS
            logger.debug(f"Searching Reddit with YARS: query='{query}', subreddit='{subreddit_query}'")

            search_results = search(
                query=query,
                subreddit=subreddit_query,
                time_filter=time_filter,
                sort="relevance",
                limit=max_results,
            )

            for post in search_results:
                try:
                    # Skip removed/deleted posts
                    if post.get("removed", False) or post.get("selftext") == "[removed]":
                        continue

                    # Extract post data
                    title = post.get("title", "")
                    selftext = post.get("selftext", "")
                    score = post.get("score", 0)
                    upvote_ratio = post.get("upvote_ratio", 0.5)
                    num_comments = post.get("num_comments", 0)
                    awards = post.get("total_awards_received", 0)
                    author = post.get("author", "[deleted]")
                    post_id = post.get("id", "")
                    subreddit = post.get("subreddit", "")
                    permalink = post.get("permalink", "")
                    created_utc = post.get("created_utc", 0)
                    flair = post.get("link_flair_text", "")

                    # Calculate engagement
                    engagement = {
                        "upvotes": score,
                        "upvote_ratio": int(upvote_ratio * 100),
                        "num_comments": num_comments,
                        "awards": awards,
                    }

                    # Calculate credibility
                    credibility = 0.5
                    if awards > 0:
                        credibility += 0.2
                    if upvote_ratio > 0.8:
                        credibility += 0.2
                    if num_comments > 50:
                        credibility += 0.1
                    credibility = min(credibility, 1.0)

                    # Calculate relevance
                    relevance = min(score / 1000, 1.0)

                    # Get post content
                    content = title
                    if selftext and len(selftext) > 0:
                        content += f"\n\n{selftext[:1000]}"  # Limit length

                    source = SourceAttribution(
                        platform="reddit",
                        url=f"https://reddit.com{permalink}" if permalink else f"https://reddit.com/r/{subreddit}/comments/{post_id}",
                        author=f"u/{author}",
                        timestamp=datetime.fromtimestamp(created_utc) if created_utc else datetime.now(),
                        engagement=engagement,
                        credibility_score=credibility,
                    )

                    result = SearchResult(
                        platform="reddit",
                        content=content,
                        source=source,
                        relevance_score=relevance,
                        metadata={
                            "post_id": post_id,
                            "subreddit": subreddit,
                            "is_self": bool(selftext),
                            "flair": flair,
                        },
                    )
                    results.append(result)

                    # Get top comments using YARS
                    try:
                        post_data = get_post(post_id=post_id, subreddit=subreddit)
                        comments = post_data.get("comments", [])[:3]  # Top 3 comments

                        for comment in comments:
                            if not comment or len(comment.get("body", "")) < 50:
                                continue

                            comment_body = comment.get("body", "")
                            comment_score = comment.get("score", 0)
                            comment_awards = comment.get("total_awards_received", 0)
                            comment_author = comment.get("author", "[deleted]")
                            comment_id = comment.get("id", "")
                            comment_created = comment.get("created_utc", 0)

                            comment_engagement = {
                                "upvotes": comment_score,
                                "awards": comment_awards,
                            }

                            comment_credibility = 0.5
                            if comment_awards > 0:
                                comment_credibility += 0.3
                            if comment_score > 100:
                                comment_credibility += 0.2
                            comment_credibility = min(comment_credibility, 1.0)

                            comment_source = SourceAttribution(
                                platform="reddit",
                                url=f"https://reddit.com{permalink}{comment_id}" if permalink else f"https://reddit.com/comments/{post_id}/_/{comment_id}",
                                author=f"u/{comment_author}",
                                timestamp=datetime.fromtimestamp(comment_created) if comment_created else datetime.now(),
                                engagement=comment_engagement,
                                credibility_score=comment_credibility,
                            )

                            comment_result = SearchResult(
                                platform="reddit",
                                content=comment_body[:1000],  # Limit length
                                source=comment_source,
                                relevance_score=min(comment_score / 500, 1.0),
                                metadata={
                                    "comment_id": comment_id,
                                    "parent_id": post_id,
                                    "subreddit": subreddit,
                                    "is_comment": True,
                                },
                            )
                            results.append(comment_result)

                    except Exception as comment_error:
                        logger.debug(f"Could not fetch comments for post {post_id}: {comment_error}")
                        # Continue without comments

                except Exception as post_error:
                    logger.warning(f"Error processing post: {post_error}")
                    continue

            logger.info(f"Retrieved {len(results)} results from Reddit (YARS) for query: {query}")
            return results[:max_results]  # Limit to max_results

        except Exception as e:
            logger.error(f"Reddit YARS error: {e}")
            return []

    def get_subreddit_suggestions(self, query: str) -> List[str]:
        """
        Suggest relevant subreddits for a query.

        Args:
            query: Search query

        Returns:
            List[str]: List of relevant subreddit names
        """
        try:
            # Common subreddits based on keywords
            suggestions = []

            # Tech-related
            if any(word in query.lower() for word in ["python", "javascript", "code", "programming", "developer"]):
                suggestions.extend(["programming", "learnprogramming", "coding"])

            # AI/ML related
            if any(word in query.lower() for word in ["ai", "machine learning", "ml", "llm", "gpt"]):
                suggestions.extend(["MachineLearning", "artificial", "LocalLLaMA"])

            # General tech
            if any(word in query.lower() for word in ["tech", "computer", "software"]):
                suggestions.extend(["technology", "software", "computers"])

            # News/current events
            if any(word in query.lower() for word in ["news", "latest", "today", "recent"]):
                suggestions.extend(["news", "worldnews"])

            # Default to popular general subreddits
            if not suggestions:
                suggestions = ["AskReddit", "all"]

            logger.debug(f"Suggested subreddits for '{query}': {suggestions[:5]}")
            return suggestions[:5]

        except Exception as e:
            logger.error(f"Error getting subreddit suggestions: {e}")
            return ["all"]
