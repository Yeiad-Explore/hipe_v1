# Setup Guide - AI Q&A Agent

Complete guide to setting up and running the AI Q&A Agent.

## Prerequisites

- Python 3.9 or higher
- Azure OpenAI account with deployments
- X (Twitter) Developer account (optional but recommended)
- Reddit Developer account (optional but recommended)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- **LangGraph** for multi-agent orchestration
- **Azure OpenAI SDK** for LLM and embeddings
- **Tweepy** for X API
- **PRAW** for Reddit API
- **ChromaDB** for vector caching
- **Rich** for beautiful CLI output

## Step 2: Configure API Credentials

### Azure OpenAI (Already Configured)

Your Azure OpenAI credentials are already set in `.env`:
- Endpoint: https://studynet-ai-agent.openai.azure.com/
- Chat Model: chat-heavy
- Embedding Model: embed-large

✅ **Azure OpenAI is ready to use!**

### X (Twitter) API Setup

1. Go to https://developer.twitter.com/
2. Create a new app or use an existing one
3. Generate API keys:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
   - Bearer Token
4. Update `.env` with your credentials:

```bash
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
X_BEARER_TOKEN=your_bearer_token_here
```

**Note:** Without X credentials, the agent will still work but won't search X/Twitter.

### Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - Name: QA Agent
   - Type: Script
   - Redirect URI: http://localhost:8080
4. Get your credentials:
   - Client ID (under app name)
   - Client Secret
5. Update `.env`:

```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

**Note:** Without Reddit credentials, the agent will still work but won't search Reddit.

## Step 3: Test the Installation

Run the test script to verify everything works:

```bash
python test_agent.py
```

Expected output:
```
Testing Q&A Agent...

1. Initializing agent...
   ✓ Agent initialized

2. Testing query...
   ✓ Query executed in 12.5s

3. Validating result...
   ✓ Result structure valid

✓ All tests passed!
```

## Step 4: Run the Agent

### Interactive Mode (Recommended)

```bash
python main.py
```

This starts an interactive CLI where you can ask multiple questions:

```
┌─────────────────────────────────────────────────┐
│ AI Q&A Agent                                    │
│ Ask questions and get answers from X and Reddit.│
│ Type 'exit' or 'quit' to exit.                 │
└─────────────────────────────────────────────────┘

Your question: What are people saying about AI?
```

### Single Query Mode

```bash
python main.py "What are people saying about AI?"
```

### Example Queries

Run pre-configured example queries:

```bash
python example.py
```

## Understanding the Output

The agent provides:

### 1. Answer
- Comprehensive synthesis from multiple sources
- Natural language, not just source summaries
- 2-4 paragraphs

### 2. Confidence Score
- **High (>70%)**: Strong consensus, reliable sources
- **Medium (40-70%)**: Some agreement, mixed reliability
- **Low (<40%)**: Conflicting info or unreliable sources

### 3. Perspectives
- **Consensus**: What most sources agree on
- **Alternative**: Conflicting or minority views
- **Expert**: Insights from high-credibility sources

### 4. Sources
- Links to original X posts and Reddit threads
- Author information
- Engagement metrics
- Credibility scores

### 5. Metadata
- Number of sources used
- Platform distribution (X vs Reddit)
- Processing time
- Consensus level

## Configuration Options

Edit `.env` to customize behavior:

```bash
# Search Configuration
MAX_SEARCH_RESULTS=20        # Results per platform
TOP_K_RETRIEVAL=10           # Top chunks for RAG
CONFIDENCE_THRESHOLD=0.6     # Minimum confidence

# Cache Configuration
CHROMA_PERSIST_DIR=./chroma_db
CACHE_TTL_HOURS=24           # Cache duration
```

## Advanced Usage

### Logging Levels

```bash
# Default (INFO)
python main.py

# Debug mode (verbose)
python main.py --log-level DEBUG

# Quiet mode
python main.py --log-level WARNING
```

### Programmatic Usage

```python
from graph.workflow import QAAgent

# Initialize
agent = QAAgent()

# Query
result = agent.query("Your question here")

# Access result
print(result["answer"])
print(f"Confidence: {result['confidence']}")

# Access sources
for source in result["sources"]:
    print(source["url"])
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    User Query                       │
└──────────────────┬──────────────────────────────────┘
                   │
          ┌────────▼─────────┐
          │ Query Analyst    │
          │ - Intent         │
          │ - Entities       │
          │ - Expand queries │
          └────────┬─────────┘
                   │
          ┌────────▼─────────┐
          │ Search           │
          │ Orchestrator     │
          │ - X search       │
          │ - Reddit search  │
          └────────┬─────────┘
                   │
          ┌────────▼─────────┐
          │ Content          │
          │ Retrieval        │
          │ - Embed          │
          │ - Rank           │
          │ - Filter         │
          └────────┬─────────┘
                   │
          ┌────────▼─────────┐
          │ Synthesis        │
          │ - Aggregate      │
          │ - Generate       │
          │ - Validate       │
          └────────┬─────────┘
                   │
          ┌────────▼─────────┐
          │  Final Answer    │
          │  with Sources    │
          └──────────────────┘
```

## Troubleshooting

### "Failed to initialize X client"
- Check X_BEARER_TOKEN in `.env`
- Verify X API credentials are valid
- Agent will continue without X search

### "Reddit API error"
- Check REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET
- Verify Reddit app is type "script"
- Agent will continue without Reddit search

### "No search results found"
- Query may be too specific
- Try rephrasing with more common terms
- Check if API rate limits are hit

### "OpenAI API error"
- Verify Azure OpenAI credentials
- Check deployment names match
- Ensure sufficient quota

### Low confidence scores
- Query may be ambiguous
- Limited information available
- Try more specific queries

## Performance Tips

1. **First query is slower** (~30s) - subsequent similar queries use cache
2. **Be specific** - Better queries get better results
3. **Use both platforms** - X for recent info, Reddit for detailed discussions
4. **Check confidence** - Low confidence means uncertain answer
5. **Review sources** - Click through to verify claims

## API Rate Limits

### X API (Free Tier)
- 50 tweets / 15 minutes
- 500 tweets / month

### Reddit API
- 60 requests / minute
- No monthly limit

### Azure OpenAI
- Depends on your deployment quota
- Embeddings are cached to reduce usage

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure API keys (Azure done, add X/Reddit)
3. ✅ Run test script
4. ✅ Try interactive mode
5. 🎯 Ask your questions!

## Support

For issues, check:
- GitHub repository
- Azure OpenAI documentation
- X Developer docs
- Reddit API docs

Happy querying! 🚀
