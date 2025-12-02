"""Reddit scraper client using snscrape."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import snscrape.modules.reddit as snreddit
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from loguru import logger

from models.schemas import SearchResult, SourceAttribution

load_dotenv()


class RedditClient:
    """Client for Reddit using snscrape (no authentication required)."""

    def __init__(self):
        """Initialize Reddit scraper client."""
        # snscrape doesn't require authentication!
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "QA_Agent/1.0")
        logger.info("Reddit snscrape client initialized (no API keys needed)")

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
        Search Reddit posts using snscrape.

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

            # Calculate time range for filtering
            time_deltas = {
                "hour": timedelta(hours=1),
                "day": timedelta(days=1),
                "week": timedelta(weeks=1),
                "month": timedelta(days=30),
                "year": timedelta(days=365),
                "all": None,
            }
            time_delta = time_deltas.get(time_filter, timedelta(days=30))
            cutoff_time = datetime.now() - time_delta if time_delta else None

            # Determine search scope
            if subreddits and len(subreddits) > 0:
                # Search specific subreddits
                for subreddit in subreddits[:3]:  # Limit to first 3 for performance
                    try:
                        logger.debug(f"Searching r/{subreddit} with snscrape: query='{query}'")
                        scraper = snreddit.RedditSearchScraper(
                            query=query,
                            subreddit=subreddit,
                        )

                        for i, submission in enumerate(scraper.get_items()):
                            if i >= max_results // len(subreddits):
                                break

                            # Apply time filter
                            if cutoff_time and submission.created < cutoff_time:
                                continue

                            result = self._process_submission(submission)
                            if result:
                                results.append(result)

                    except Exception as sub_error:
                        logger.warning(f"Error searching r/{subreddit}: {sub_error}")
                        continue
            else:
                # Search all of Reddit
                logger.debug(f"Searching all of Reddit with snscrape: query='{query}'")
                scraper = snreddit.RedditSearchScraper(query=query)

                for i, submission in enumerate(scraper.get_items()):
                    if i >= max_results:
                        break

                    # Apply time filter
                    if cutoff_time and submission.created < cutoff_time:
                        continue

                    result = self._process_submission(submission)
                    if result:
                        results.append(result)

            logger.info(f"Retrieved {len(results)} results from Reddit (snscrape) for query: {query}")
            return results[:max_results]

        except Exception as e:
            logger.error(f"Reddit snscrape error: {e}")
            return []

    def _process_submission(self, submission) -> Optional[SearchResult]:
        """
        Process a Reddit submission into a SearchResult.

        Args:
            submission: snscrape RedditSubmission object

        Returns:
            SearchResult or None if processing fails
        """
        try:
            # Extract data from submission
            title = submission.title or ""
            selftext = submission.selftext or ""
            score = submission.score or 0
            num_comments = submission.commentCount or 0
            author = submission.author or "[deleted]"
            post_id = submission.id or ""
            subreddit = submission.subreddit or ""
            url = submission.url or f"https://reddit.com/r/{subreddit}/comments/{post_id}"
            created = submission.created or datetime.now()

            # Skip removed/deleted posts
            if selftext in ["[removed]", "[deleted]"] or title in ["[removed]", "[deleted]"]:
                return None

            # Calculate engagement (estimate upvote ratio)
            upvote_ratio = 0.8  # Default estimate
            if score > 0:
                upvote_ratio = min(0.9, 0.5 + (score / 1000))

            engagement = {
                "upvotes": score,
                "upvote_ratio": int(upvote_ratio * 100),
                "num_comments": num_comments,
                "awards": 0,  # snscrape doesn't provide awards
            }

            # Calculate credibility
            credibility = 0.5
            if upvote_ratio > 0.8:
                credibility += 0.2
            if num_comments > 50:
                credibility += 0.1
            if score > 100:
                credibility += 0.2
            credibility = min(credibility, 1.0)

            # Calculate relevance
            relevance = min(score / 1000, 1.0)

            # Get post content
            content = title
            if selftext and len(selftext) > 0:
                content += f"\n\n{selftext[:1000]}"  # Limit length

            source = SourceAttribution(
                platform="reddit",
                url=url,
                author=f"u/{author}",
                timestamp=created,
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
                    "flair": "",  # snscrape doesn't provide flair
                },
            )

            return result

        except Exception as e:
            logger.warning(f"Error processing submission: {e}")
            return None

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

            query_lower = query.lower()

            # Tech-related
            if any(word in query_lower for word in ["python", "javascript", "code", "programming", "developer", "coding"]):
                suggestions.extend(["programming", "learnprogramming", "coding", "Python", "javascript"])

            # AI/ML related
            if any(word in query_lower for word in ["ai", "machine learning", "ml", "llm", "gpt", "artificial intelligence"]):
                suggestions.extend(["MachineLearning", "artificial", "LocalLLaMA", "ChatGPT", "OpenAI"])

            # General tech
            if any(word in query_lower for word in ["tech", "computer", "software", "hardware"]):
                suggestions.extend(["technology", "software", "computers", "gadgets"])

            # News/current events
            if any(word in query_lower for word in ["news", "latest", "today", "recent", "happening"]):
                suggestions.extend(["news", "worldnews", "tech"])

            # Web development
            if any(word in query_lower for word in ["web", "frontend", "backend", "react", "node"]):
                suggestions.extend(["webdev", "reactjs", "node", "Frontend", "Backend"])

            # Mobile development
            if any(word in query_lower for word in ["android", "ios", "mobile", "app"]):
                suggestions.extend(["androiddev", "iOSProgramming", "mobiledev", "FlutterDev"])

            # Data science
            if any(word in query_lower for word in ["data", "science", "analytics", "visualization"]):
                suggestions.extend(["datascience", "dataengineering", "analytics"])

            # Gaming
            if any(word in query_lower for word in ["game", "gaming", "video game"]):
                suggestions.extend(["gaming", "Games", "pcgaming"])

            # Business/Career
            if any(word in query_lower for word in ["career", "job", "work", "salary", "interview"]):
                suggestions.extend(["cscareerquestions", "programming", "jobs"])

            # Default to popular general subreddits if no matches
            if not suggestions:
                suggestions = ["AskReddit", "technology", "news"]

            # Remove duplicates while preserving order
            seen = set()
            unique_suggestions = []
            for sub in suggestions:
                if sub not in seen:
                    seen.add(sub)
                    unique_suggestions.append(sub)

            logger.debug(f"Suggested subreddits for '{query}': {unique_suggestions[:5]}")
            return unique_suggestions[:5]

        except Exception as e:
            logger.error(f"Error getting subreddit suggestions: {e}")
            return ["all"]
