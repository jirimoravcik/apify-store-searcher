# Apify Store Searcher

A web application to search and browse the [Apify Store](https://apify.com/store) with ML-enhanced category filtering.

## Try It

**Live URL:** https://jirimoravcik--apify-store-searcher.apify.actor

Just open the link and start searching for Actors by name, category, or description.

## Features

- **Full-text search** across all Actors in the Apify Store
- **ML-powered category ranking** using TF-IDF and cosine similarity to surface the most relevant Actors per category
- **Smart agent detection** - distinguishes true AI agents from scrapers that are miscategorized
- **Neobrutalist UI** with Apify's brand colors
- **Real-time search** with instant results
- **Standby mode** for always-on deployment on Apify platform

## How It Works

### ML Classification

The Actor fetches all Actors from the Apify Store API and computes ML relevance scores for each category using:

1. **TF-IDF Vectorization** - Converts Actor titles, descriptions, and metadata into numerical vectors
2. **Exemplar Matching** - Compares each Actor against hand-crafted exemplar descriptions for each category
3. **Cosine Similarity** - Ranks Actors by how closely they match the category exemplars
4. **Metadata Signals** - Applies adjustments based on:
   - Keywords in title/description (e.g., "agent", "scraper", "LLM")
   - Agentic payments whitelist status
   - MCP/Model Context Protocol mentions
   - Quality signals (user count, ratings, reviews)

This approach is particularly effective at filtering the **Agents** category, where many scrapers are miscategorized. True AI agents (with LLM integration, autonomous behavior, tool calling) are ranked higher than simple web scrapers.

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   HTTP Server    │────▶│   Store Cache   │
│   (HTML/JS)     │     │   (Python)       │     │   (In-memory)   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  ML Classifier  │
                                                 │  (TF-IDF)       │
                                                 └─────────────────┘
```

- **Frontend**: Neobrutalist single-page app with search and category filters
- **HTTP Server**: Handles API requests and serves the frontend
- **Store Cache**: Fetches all Actors from API, caches with auto-refresh every 5 minutes
- **ML Classifier**: Computes category relevance scores using TF-IDF similarity

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Serves the web frontend |
| `GET /api/search` | Search Actors with optional filters |
| `GET /api/cache-stats` | Get cache statistics |
| `GET /health` | Health check endpoint |

### Search Parameters

- `q` - Search query (searches title, description, username)
- `category` - Filter by category (e.g., `AGENTS`, `AI`, `SOCIAL_MEDIA`)
- `limit` - Max results to return (default: 50, max: 100)
- `offset` - Pagination offset (default: 0)

## Categories

The following categories are supported:

| Category | Description |
|----------|-------------|
| `AGENTS` | AI agents with LLM integration and autonomous capabilities |
| `AI` | Machine learning and AI-powered tools |
| `SOCIAL_MEDIA` | Social media scrapers and tools |
| `LEAD_GENERATION` | Business contact and lead finding tools |
| `ECOMMERCE` | E-commerce and product data tools |
| `SEO_TOOLS` | SEO analysis and monitoring |
| `JOBS` | Job listing scrapers |
| `MCP_SERVERS` | Model Context Protocol servers |
| `NEWS` | News and media scrapers |
| `REAL_ESTATE` | Property and real estate data |
| `DEVELOPER_TOOLS` | Developer utilities |
| `TRAVEL` | Travel and booking data |
| `VIDEOS` | Video platform tools |
| `AUTOMATION` | Workflow automation tools |
| `INTEGRATIONS` | Platform integration tools |
| `OPEN_SOURCE` | Open source tools |
| `OTHER` | Miscellaneous tools |

## Local Development

### Prerequisites

- Python 3.10+
- [Apify CLI](https://docs.apify.com/cli/)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd apify-store-searcher

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
apify run
```

The server will start at `http://localhost:8080`.

## Deployment

### Deploy to Apify Platform

```bash
# Login to Apify (requires API token)
apify login

# Deploy the Actor
apify push
```

The Actor runs in **standby mode**, staying alive to serve requests with low latency.

## Tech Stack

- **Python 3.10+** - Runtime
- **Apify SDK** - Actor framework and storage
- **scikit-learn** - TF-IDF vectorization and cosine similarity
- **NumPy** - Numerical computations
- **httpx** - Async HTTP client

## License

ISC
