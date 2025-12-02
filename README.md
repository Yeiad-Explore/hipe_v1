# AI Q&A Agent with LangGraph

An advanced AI-powered Q&A agent that searches X (Twitter) and Reddit to provide comprehensive, multi-source answers using Azure OpenAI and LangGraph.

## Features

- 🤖 **Multi-Agent Architecture**: Query Analyst, Search Orchestrator, Content Retrieval, and Synthesis agents
- 🔍 **Intelligent Search**: Hybrid search across X and Reddit with semantic understanding
- 🧠 **RAG Pipeline**: Semantic search with embeddings and vector caching
- 💬 **Conversational Memory**: Handles follow-up questions with context
- ⚡ **Confidence Scoring**: Transparent reliability metrics for answers
- 🎯 **Smart Routing**: Auto-detects which platform to prioritize based on query type

## Architecture

```
User Query
    ↓
Query Analyst Agent (intent classification, entity extraction, query expansion)
    ↓
Search Orchestrator Agent (decides X, Reddit, or both)
    ↓
Content Retrieval Agent (parallel search, ranking, filtering)
    ↓
Synthesis Agent (multi-document synthesis, answer generation)
    ↓
Final Answer (with sources, confidence, perspectives)
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env` file with your API credentials:
   - Azure OpenAI (already configured)
   - X (Twitter) API keys
   - Reddit API keys

3. Run the agent:
```bash
python main.py
```

## Configuration

Edit `.env` to customize:
- `MAX_SEARCH_RESULTS`: Number of results to fetch per platform
- `TOP_K_RETRIEVAL`: Number of top chunks for RAG
- `CONFIDENCE_THRESHOLD`: Minimum confidence for answers
- `CACHE_TTL_HOURS`: Cache duration for repeated queries

## Usage

```python
from agent import QAAgent

agent = QAAgent()
result = agent.query("What are people saying about the latest iPhone?")
print(result["answer"])
print(f"Confidence: {result['confidence']}")
print(f"Sources: {result['sources']}")
```

## Project Structure

```
hipe_v1/
├── agents/              # LangGraph agent implementations
│   ├── query_analyst.py
│   ├── search_orchestrator.py
│   ├── content_retrieval.py
│   └── synthesis.py
├── clients/             # API clients
│   ├── azure_openai.py
│   ├── x_client.py
│   └── reddit_client.py
├── models/              # Data models
│   └── schemas.py
├── utils/               # Utilities
│   ├── embeddings.py
│   ├── vector_store.py
│   └── logger.py
├── graph/               # LangGraph workflow
│   └── workflow.py
├── main.py              # CLI interface
└── requirements.txt
```

## Advanced Features

- **Query Expansion**: Generates semantic variations for better coverage
- **Re-ranking**: Cross-encoder re-ranking for relevance
- **Diversity Sampling**: MMR for varied perspectives
- **Hallucination Detection**: Validates claims against sources
- **Multi-modal Support**: Handles images and videos (planned)

## License

MIT
