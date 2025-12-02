"""Reddit client using public JSON API (no authentication required)."""
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from loguru import logger

from models.schemas import SearchResult, SourceAttribution

load_dotenv()


class RedditClient:
    """Client for Reddit using public JSON API (no authentication required)."""

    def __init__(self):
        """Initialize Reddit client."""
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "QA_Agent/1.0")
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent
        })
        logger.info("Reddit JSON API client initialized (no API keys needed)")

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
        Search Reddit posts using public JSON API.

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
            if subreddits and len(subreddits) > 0:
                # Search specific subreddits
                subreddit_str = "+".join(subreddits[:5])  # Max 5 subreddits
            else:
                subreddit_str = "all"

            # Build search URL
            search_url = f"{self.base_url}/r/{subreddit_str}/search.json"

            params = {
                "q": query,
                "sort": "relevance",
                "t": time_filter,
                "limit": min(max_results, 100),  # Reddit limit
                "restrict_sr": "on",
                "raw_json": 1,
            }

            logger.debug(f"Searching Reddit: {search_url} with params {params}")

            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "data" not in data or "children" not in data["data"]:
                logger.warning(f"No results found for query: {query}")
                return []

            posts = data["data"]["children"]

            for post_data in posts:
                if post_data["kind"] != "t3":  # t3 = link/post
                    continue

                post = post_data["data"]
                result = self._process_post(post)
                if result:
                    results.append(result)

            logger.info(f"Retrieved {len(results)} results from Reddit for query: {query}")

            # Add small delay to be respectful
            time.sleep(0.5)

            return results[:max_results]

        except requests.exceptions.RequestException as e:
            logger.error(f"Reddit API request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Reddit search error: {e}")
            return []

    def _process_post(self, post: Dict[str, Any]) -> Optional[SearchResult]:
        """
        Process a Reddit post into a SearchResult.

        Args:
            post: Reddit post data dictionary

        Returns:
            SearchResult or None if processing fails
        """
        try:
            # Extract data
            title = post.get("title", "")
            selftext = post.get("selftext", "")
            score = post.get("score", 0)
            upvote_ratio = post.get("upvote_ratio", 0.5)
            num_comments = post.get("num_comments", 0)
            author = post.get("author", "[deleted]")
            post_id = post.get("id", "")
            subreddit = post.get("subreddit", "")
            permalink = post.get("permalink", "")
            created_utc = post.get("created_utc", 0)
            link_flair_text = post.get("link_flair_text", "")
            total_awards = post.get("total_awards_received", 0)

            # Skip removed/deleted posts
            if selftext in ["[removed]", "[deleted]"] or title in ["[removed]", "[deleted]"]:
                return None

            if author in ["[deleted]", "AutoModerator"]:
                return None

            # Calculate engagement
            engagement = {
                "upvotes": score,
                "upvote_ratio": int(upvote_ratio * 100),
                "num_comments": num_comments,
                "awards": total_awards,
            }

            # Calculate credibility
            credibility = 0.5
            if total_awards > 0:
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
                url=f"{self.base_url}{permalink}",
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
                    "flair": link_flair_text,
                },
            )

            return result

        except Exception as e:
            logger.warning(f"Error processing post: {e}")
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
                suggestions.extend(["news", "worldnews", "technology"])

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

    def get_post_comments(self, post_id: str, subreddit: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top comments for a post (optional enhancement).

        Args:
            post_id: Reddit post ID
            subreddit: Subreddit name
            limit: Number of comments to retrieve

        Returns:
            List of comment dictionaries
        """
        try:
            url = f"{self.base_url}/r/{subreddit}/comments/{post_id}.json"
            params = {"limit": limit, "raw_json": 1}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if len(data) < 2:
                return []

            comments = []
            comment_listing = data[1]["data"]["children"]

            for comment_data in comment_listing[:limit]:
                if comment_data["kind"] == "t1":  # t1 = comment
                    comment = comment_data["data"]
                    if comment.get("body") and comment["body"] not in ["[removed]", "[deleted]"]:
                        comments.append({
                            "body": comment.get("body", ""),
                            "score": comment.get("score", 0),
                            "author": comment.get("author", "[deleted]"),
                        })

            time.sleep(0.5)  # Be respectful
            return comments

        except Exception as e:
            logger.debug(f"Error fetching comments: {e}")
            return []
