# PLAN: Reddit Customer Development Tool

## Executive Summary

Build a Python 3.14 application to search Reddit for customer pain points and market opportunities. The tool will scrape Reddit posts and comments, analyze them for keywords indicating problems people would pay to solve, and generate interactive visualizations to identify profitable solopreneur niches.

## Use Case

**Goal**: Customer development for solopreneurship - find pain points that represent app opportunities

**Example searches**:
- Keywords: "pay for", "wish there was", "need a tool", "struggling with"
- Subreddits: r/SaaS, r/Entrepreneur, r/startups, r/smallbusiness
- Analysis: What problems are people frustrated with? What would they pay for?

**Output**: Interactive HTML dashboard showing:
- Keyword frequency and trends over time
- Topic clusters (e.g., "marketing tools", "productivity apps")
- Sentiment analysis (frustration levels)
- Extracted context around pain points with payment signals

## Project Requirements

### Functional Requirements

1. **Search Capabilities**
   - Search by configurable keyword phrases
   - Target specific subreddits (configurable list)
   - Search both posts AND comments (multi-level threads)
   - Time-based filtering (last N days)
   - Score/popularity filtering (min upvotes)

2. **Data Collection**
   - Use PRAW (Python Reddit API Wrapper)
   - Handle multi-level comment trees
   - Extract full paragraph context around keywords
   - Deduplicate previously seen threads
   - Store in SQLite database

3. **Rate Limit Management**
   - Reddit OAuth limit: 60 requests/minute
   - Conservative approach with automatic exponential backoff
   - Resumable searches (save state, continue if interrupted)
   - Progress tracking and logging

4. **Analysis Features**
   - **Keyword frequency**: Count mentions, find trending phrases
   - **Topic clustering**: Group similar problems using ML (scikit-learn)
   - **Sentiment analysis**: Measure frustration/urgency (transformers)
   - **Context extraction**: Pull surrounding text to understand full problem

5. **Visualization**
   - Interactive HTML dashboards (Plotly charts)
   - No server required (standalone HTML files)
   - Charts: keyword trends, topic clusters, sentiment distribution, co-occurrence networks
   - Exportable data (JSON, CSV)

6. **Interface**
   - CLI with arguments (Click framework)
   - Example: `python main.py search --keywords "pay for" --subreddits SaaS,Entrepreneur --days 30`
   - Commands: search, report, list-searches, resume, config

### Non-Functional Requirements

- **Python 3.14** compatible
- **Medium scale**: Handle hundreds of threads per search
- **Storage**: SQLite (queryable, portable, full-text search)
- **Error handling**: Network failures, API errors, deleted content
- **State management**: Resumable searches with JSON state files
- **Configuration**: YAML for subreddit lists, .env for credentials
- **Logging**: Rich console output with progress bars

## Technical Architecture

### Project Structure

```
redditsearch/
├── main.py                          # CLI entry point
├── pyproject.toml                   # Dependencies
├── .env.example                     # Credential template
├── .env                            # User credentials (gitignored)
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Pydantic settings
│   └── sources/                    # Source-specific configs
│       ├── reddit.yaml             # Reddit subreddit groups
│       ├── twitter.yaml            # Twitter lists (future)
│       └── hackernews.yaml         # HN topics (future)
├── src/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py             # Click commands
│   │   └── validators.py           # Input validation
│   ├── sources/                    # Pluggable data source modules
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract base classes
│   │   ├── reddit/
│   │   │   ├── __init__.py
│   │   │   ├── client.py           # Reddit-specific client (PRAW)
│   │   │   ├── parser.py           # Reddit comment tree parsing
│   │   │   └── models.py           # Reddit-specific data models
│   │   ├── twitter/                # Future: Twitter/X support
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── parser.py
│   │   ├── hackernews/             # Future: HackerNews support
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── parser.py
│   │   └── discord/                # Future: Discord support
│   │       ├── __init__.py
│   │       ├── client.py
│   │       └── parser.py
│   ├── core/                       # Source-agnostic core functionality
│   │   ├── __init__.py
│   │   ├── semantic_matcher.py     # Semantic similarity (all sources)
│   │   ├── rate_limiter.py         # Generic rate limiting
│   │   ├── search_engine.py        # Orchestrates multi-source searches
│   │   └── content_processor.py    # Process content from any source
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── models.py               # Generic models (Post, Reply, Match)
│   │   ├── database.py             # DB connection
│   │   └── repositories.py         # Data access layer
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── keyword_analyzer.py     # Frequency & trending
│   │   ├── topic_clusterer.py      # ML clustering (sklearn)
│   │   ├── sentiment_analyzer.py   # Sentiment (transformers)
│   │   └── context_extractor.py    # Context extraction
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── dashboard.py            # Dashboard generator
│   │   ├── charts.py               # Plotly charts
│   │   └── templates/
│   │       └── report.html         # Jinja2 template
│   └── utils/
│       ├── __init__.py
│       ├── logger.py               # Logging config
│       └── state_manager.py        # Resume capability
├── data/
│   ├── redditsearch.db            # SQLite database
│   └── state/                      # Search state files
├── output/
│   └── reports/                    # Generated HTML
└── tests/
    ├── __init__.py
    ├── test_sources/               # Test each source plugin
    │   ├── test_reddit.py
    │   ├── test_base.py
    │   └── test_twitter.py
    ├── test_core.py
    ├── test_storage.py
    └── test_analysis.py
```

### Key Dependencies (pyproject.toml)

**Reddit & Web**:
- `praw>=7.7.1` - Reddit API client
- `tenacity>=8.2.0` - Retry logic with exponential backoff

**Database**:
- `sqlalchemy>=2.0.0` - ORM
- `alembic>=1.13.0` - Database migrations

**CLI & Config**:
- `click>=8.1.0` - CLI framework
- `rich>=13.7.0` - Beautiful terminal output
- `python-dotenv>=1.0.0` - Environment variables
- `pyyaml>=6.0.0` - YAML config files
- `pydantic>=2.5.0` - Settings validation

**Analysis & NLP**:
- `transformers>=4.36.0` - Sentiment analysis models
- `torch>=2.1.0` - PyTorch (for transformers)
- `scikit-learn>=1.4.0` - Topic clustering
- `nltk>=3.8.0` - Text preprocessing
- `sentence-transformers>=2.2.0` - Semantic similarity

**Visualization**:
- `plotly>=5.18.0` - Interactive charts
- `jinja2>=3.1.0` - HTML templating
- `pandas>=2.1.0` - Data manipulation
- `tqdm>=4.66.0` - Progress bars

**Testing & Development** (optional dependencies):
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Code coverage reporting
- `pytest-mock>=3.12.0` - Mocking support
- `black>=23.12.0` - Code formatting
- `ruff>=0.1.0` - Fast linting

### Database Schema

**Core Tables** (Source-Agnostic Design):

1. **searches** - Track each search operation
   - Fields: search_id (UUID), keywords (JSON), sources (JSON), source_targets (JSON), time_filter, min_score, status, timestamps
   - Purpose: Resume capability, search history
   - Note: `sources` = ['reddit', 'twitter'], `source_targets` = {'reddit': ['SaaS', 'Entrepreneur'], 'twitter': ['#startups']}

2. **posts** - Top-level content (Reddit submissions, tweets, HN posts)
   - Fields: post_id (int PK), source (str), source_id (unique per source), title, body, author, source_location (subreddit/hashtag/etc), url, score, reply_count, created_utc
   - Deduplication: Unique constraint on (source, source_id)
   - Indexes: (source, created_utc, score), (source_location, created_utc)
   - Examples:
     - Reddit: source='reddit', source_location='r/SaaS'
     - Twitter: source='twitter', source_location='#startups'
     - HN: source='hackernews', source_location='Show HN'

3. **replies** - Nested responses (Reddit comments, tweet replies, HN comments)
   - Fields: reply_id (int PK), source (str), source_id (unique per source), post_id (FK), parent_id (nullable FK to replies), body, author, score, depth
   - Indexes: (post_id, depth) for tree queries
   - Supports multi-level threading across all sources

4. **keyword_matches** - Where keywords found with context
   - Fields: search_id (FK), keyword, source (str), post_id (nullable FK), reply_id (nullable FK), match_type, match_score (float for semantic similarity), context_before, matched_text, context_after, full_paragraph, embedding (optional: vector representation)
   - Purpose: Store extracted context for analysis
   - Indexes: (keyword, search_id), (match_score), (source)

5. **analysis_results** - Cached analysis outputs
   - Fields: search_id (FK), analysis_type, results (JSON), generated_at
   - Purpose: Avoid re-running expensive ML analyses

6. **topics** - Discovered topic clusters
   - Fields: search_id (FK), topic_label, keywords, num_matches, avg_sentiment

### Rate Limiting Strategy

**Conservative Adaptive Approach**:

1. **Initial rate**: 0.5 req/sec (30 req/min) - 50% of limit
2. **Track successes**: After 10 consecutive successes, speed up by 10%
3. **On rate limit error**:
   - Use Reddit's `Retry-After` header if provided
   - Otherwise: exponential backoff (multiply delay by 2)
   - Cap at 60 seconds between requests
4. **PRAW configuration**: `ratelimit_seconds=300` for built-in handling
5. **Retry logic**: Max 5 attempts with exponential wait (1s, 2s, 4s, 8s, 16s)

**Implementation** (`rate_limiter.py`):
```python
class AdaptiveRateLimiter:
    - current_delay starts at 2.0s
    - wait() before each request
    - on_success() gradually speeds up
    - on_rate_limit() exponential backoff
```

### CLI Commands

**Primary Commands**:

```bash
# Search Reddit (exact keyword matching)
redditsearch search \
  --keywords "pay for,wish there was,need a tool" \
  --subreddits "SaaS,Entrepreneur,startups" \
  --days 30 \
  --min-score 5 \
  --max-posts 100

# Search with semantic similarity (finds similar phrases)
redditsearch search \
  --keywords "pay for" \
  --search-mode semantic \
  --similarity-threshold 0.75 \
  --subreddits "SaaS,Entrepreneur" \
  --days 30

# Hybrid search (exact + semantic)
redditsearch search \
  --keywords "pay for,need a tool" \
  --search-mode hybrid \
  --subreddits "SaaS" \
  --days 7

# Generate report for a search
redditsearch report <search_id> --format html

# List recent searches
redditsearch list-searches --days 7

# Resume interrupted search
redditsearch resume <search_id>

# Show current config
redditsearch config
```

### Analysis Pipeline

**Four Analysis Types**:

1. **Keyword Frequency** (`keyword_analyzer.py`)
   - Count keyword occurrences
   - Score-weighted frequency (weight by upvotes)
   - Temporal trends (mentions over time)
   - Co-occurrence matrix (keywords appearing together)

2. **Topic Clustering** (`topic_clusterer.py`)
   - TF-IDF vectorization of matched paragraphs
   - K-means clustering (5 clusters default)
   - Extract top terms per cluster
   - Label topics by dominant keywords

3. **Sentiment Analysis** (`sentiment_analyzer.py`)
   - Use pre-trained model: `cardiffnlp/twitter-roberta-base-sentiment-latest`
   - Analyze full paragraph context
   - Aggregate by keyword
   - Extract high-negative examples (strong pain points)

4. **Context Extraction** (`context_extractor.py`)
   - Rank contexts by score/engagement
   - Find pain point indicators: "frustrated", "struggling", "impossible"
   - Find payment signals: "pay for", "would buy", "worth paying"
   - Extract and rank most relevant contexts

### Visualization Dashboard

**Plotly Charts** (interactive, standalone HTML):

1. **Keyword Frequency** - Horizontal bar chart (top 20)
2. **Keyword Timeline** - Line chart (mentions over time)
3. **Topic Clusters** - 2D scatter plot (t-SNE projection)
4. **Sentiment Distribution** - Pie chart (pos/neg/neutral)
5. **Sentiment by Keyword** - Grouped bar chart
6. **Co-occurrence Network** - Network graph (connected keywords)
7. **Top Contexts** - Interactive table (sortable, searchable)
8. **Engagement vs Sentiment** - Scatter plot

**Template** (`templates/report.html`):
- Jinja2 template with embedded Plotly charts
- Summary statistics section
- Export buttons (JSON, CSV)
- Responsive design

### Configuration Management

**Environment Variables** (`.env`):
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=reddit-customer-dev:v0.1.0 (by /u/YOUR_USERNAME)
```

**Subreddit Groups** (`config/subreddits.yaml`):
```yaml
groups:
  entrepreneurship:
    - SaaS
    - Entrepreneur
    - startups
    - smallbusiness
    - Bootstrapped

presets:
  pain_points:
    keywords: ["struggling with", "frustrated", "wish there was"]
    subreddits: entrepreneurship
    days: 30
```

**Settings** (`config/settings.py`):
- Pydantic-based validation
- Load from .env
- Defaults for rate limits, search params, output paths
- Semantic search configuration:
  - `SEMANTIC_MODEL`: Default model (all-MiniLM-L6-v2)
  - `SEMANTIC_THRESHOLD`: Default similarity threshold (0.75)
  - `SEARCH_MODE`: Default search mode (hybrid)

### Error Handling

**Layered Approach**:

1. **Network/API Level**: Retry with exponential backoff (tenacity)
2. **Data Validation**: Handle deleted/removed content gracefully
3. **Search Orchestration**: Continue with other subreddits if one fails
4. **CLI Level**: User-friendly error messages, suggest resume command

**Specific Scenarios**:
- Deleted content: Check for `[deleted]` author, null bodies
- Rate limits: Automatic backoff + save state for resume
- Network failures: 5 retries with exponential wait
- Incomplete comment trees: Use PRAW `replace_more(limit=32)`

### State Management (Resumability)

**State Files** (`data/state/<search_id>.json`):
```json
{
  "search_id": "abc-123",
  "status": "running",
  "progress": {
    "subreddits_completed": ["SaaS", "Entrepreneur"],
    "subreddits_pending": ["startups"],
    "posts_processed": 87,
    "comments_processed": 543
  },
  "processed_posts": ["post_id_1", "post_id_2", ...],
  "errors": []
}
```

**Resume Logic**:
1. Load state file
2. Check `processed_posts` to skip duplicates
3. Continue with `subreddits_pending`
4. Update state every 10 posts

## Implementation Phases

### Phase 1: Core Infrastructure
**Files to create**:
- Update `pyproject.toml` with all dependencies (including dev dependencies)
- Create `config/settings.py` with Pydantic settings
- Create `config/subreddits.yaml` with default lists
- Create `.env.example` template
- Setup `src/` package structure (with `__init__.py` files)
- Implement `src/utils/logger.py`
- Create `tests/test_config.py` - Test settings loading and validation
- Create `pytest.ini` - Pytest configuration

**Testing**:
- Test that settings load correctly from .env
- Test YAML config parsing
- Test logger initialization
- Run: `pytest tests/test_config.py -v`

**Git checkpoint**:
```bash
pytest tests/test_config.py -v
git add .
git commit -m "Phase 1: Core infrastructure and configuration"
git push origin main
```

### Phase 2: Database Layer
**Files to create**:
- `src/storage/models.py` - SQLAlchemy ORM models (Submission, Comment, KeywordMatch, Search, Topic, AnalysisResult)
- `src/storage/database.py` - Database connection, session management
- `src/storage/repositories.py` - Repository pattern for data access
- `alembic.ini` and migrations for schema setup
- `tests/test_storage.py` - Test models, database operations, repositories

**Testing**:
- Test model creation and relationships
- Test repository CRUD operations
- Test deduplication logic (get_or_create_submission)
- Test database migrations
- Run: `pytest tests/test_storage.py -v`

**Git checkpoint**:
```bash
pytest tests/test_storage.py -v
git add .
git commit -m "Phase 2: Database models and migrations"
git push origin main
```

### Phase 3: Data Sources & Core Search
**Files to create**:
- `src/sources/base.py` - Abstract base classes (DataSourcePlugin, SourcePost, SourceReply)
- `src/sources/reddit/__init__.py` - Reddit plugin module
- `src/sources/reddit/client.py` - Reddit plugin implementation (PRAW)
- `src/sources/reddit/parser.py` - Reddit comment tree parsing
- `src/core/rate_limiter.py` - Generic adaptive rate limiting
- `src/core/semantic_matcher.py` - Semantic similarity matching using sentence-transformers
- `src/core/search_engine.py` - Multi-source search orchestration
- `src/core/content_processor.py` - Process and normalize content from any source
- `src/utils/state_manager.py` - State tracking for resume
- `tests/test_sources/test_base.py` - Test plugin interface
- `tests/test_sources/test_reddit.py` - Test Reddit plugin
- `tests/test_core.py` - Test core functionality

**Testing**:
- Test plugin base interface contract
- Test Reddit plugin authentication and search
- Test Reddit comment tree traversal with mocked PRAW
- Test rate limiter delays and backoff logic
- Test exact keyword matching and context extraction
- Test semantic similarity matching with known examples
- Test hybrid search mode (exact + semantic)
- Test multi-source search engine orchestration
- Test state manager save/resume functionality
- Run: `pytest tests/test_sources/ tests/test_core.py -v`

**Git checkpoint**:
```bash
pytest tests/test_sources/ tests/test_core.py -v
git add .
git commit -m "Phase 3: Plugin architecture with Reddit implementation"
git push origin main
```

### Phase 4: CLI Interface
**Files to create**:
- Update `main.py` - Entry point with Click app
- `src/cli/commands.py` - Command implementations (search, report, list, resume)
- `src/cli/validators.py` - Input validation helpers
- `tests/test_cli.py` - Test CLI commands and validators

**Testing**:
- Test CLI command parsing and validation
- Test error handling for invalid inputs
- Test command execution with mocked dependencies
- Use Click's CliRunner for testing
- Run: `pytest tests/test_cli.py -v`

**Git checkpoint**:
```bash
pytest tests/test_cli.py -v
git add .
git commit -m "Phase 4: CLI interface with Click commands"
git push origin main
```

### Phase 5: Analysis Pipeline
**Files to create**:
- `src/analysis/keyword_analyzer.py` - Frequency, trends, co-occurrence
- `src/analysis/topic_clusterer.py` - K-means clustering with TF-IDF
- `src/analysis/sentiment_analyzer.py` - Transformers-based sentiment
- `src/analysis/context_extractor.py` - Extract and rank contexts
- `tests/test_analysis.py` - Test all analysis modules

**Testing**:
- Test keyword frequency calculations
- Test co-occurrence matrix generation
- Test topic clustering with sample data
- Test sentiment analysis with known examples
- Test context extraction and ranking
- Run: `pytest tests/test_analysis.py -v`

**Git checkpoint**:
```bash
pytest tests/test_analysis.py -v
git add .
git commit -m "Phase 5: Analysis pipeline (NLP and ML)"
git push origin main
```

### Phase 6: Visualization
**Files to create**:
- `src/visualization/charts.py` - Plotly chart builders
- `src/visualization/templates/report.html` - Jinja2 HTML template
- `src/visualization/dashboard.py` - Dashboard generator (runs analyses, builds charts, renders HTML)
- `tests/test_visualization.py` - Test chart generation and dashboard

**Testing**:
- Test chart creation with sample data
- Test HTML template rendering
- Test dashboard generation end-to-end
- Verify generated HTML is valid
- Run: `pytest tests/test_visualization.py -v`

**Git checkpoint**:
```bash
pytest tests/test_visualization.py -v
git add .
git commit -m "Phase 6: Interactive visualizations and dashboards"
git push origin main
```

### Phase 7: Integration Testing & Documentation
**Files to create**:
- `tests/test_integration.py` - End-to-end integration tests
- `tests/conftest.py` - Shared pytest fixtures
- Update `README.md` - Complete usage guide, setup instructions, examples
- Update `CLAUDE.md` - Development guide with architecture details

**Testing**:
- Run full integration tests (search -> analyze -> visualize)
- Test with mock Reddit data end-to-end
- Run full test suite with coverage: `pytest --cov=src --cov-report=html`
- Verify coverage is >80%
- Run linting: `ruff check src/`
- Run formatting: `black src/ tests/`

**Git checkpoint**:
```bash
pytest --cov=src --cov-report=html
ruff check src/
black src/ tests/ --check
git add .
git commit -m "Phase 7: Integration tests and documentation complete"
git push origin main
```

## Critical Implementation Details

### 1. Semantic Search Implementation

**Purpose**: Find semantically similar content beyond exact keyword matches.

**Use Cases**:
- "pay for" also finds: "willing to spend money on", "would buy", "shut up and take my money"
- "need a tool" also finds: "looking for a solution", "wish there was an app", "desperately need software"
- "frustrated with" also finds: "annoyed by", "hate dealing with", "this is driving me crazy"

**Implementation** (`src/scraper/semantic_matcher.py`):
```python
from sentence_transformers import SentenceTransformer, util

class SemanticMatcher:
    """Find semantically similar text using embeddings"""

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Lightweight model: 384 dimensions, ~80MB
        self.model = SentenceTransformer(model_name)

    def encode_query(self, query: str):
        """Convert query to vector embedding"""
        return self.model.encode(query, convert_to_tensor=True)

    def find_similar(self, query_embedding, texts: list, threshold=0.7):
        """
        Find texts semantically similar to query

        Args:
            query_embedding: Pre-encoded query vector
            texts: List of text strings to search
            threshold: Similarity threshold (0.0-1.0, default 0.7)

        Returns:
            List of (text, similarity_score) tuples above threshold
        """
        text_embeddings = self.model.encode(texts, convert_to_tensor=True)
        similarities = util.cos_sim(query_embedding, text_embeddings)[0]

        matches = []
        for idx, score in enumerate(similarities):
            if score >= threshold:
                matches.append((texts[idx], float(score)))

        return sorted(matches, key=lambda x: x[1], reverse=True)
```

**Search Modes**:

1. **Exact Mode** (default):
   - Traditional case-insensitive string matching
   - Fast, precise
   - Use: `--search-mode exact`

2. **Semantic Mode**:
   - Encode query as embedding
   - Compare to all text using cosine similarity
   - Return matches above threshold (default: 0.75)
   - Use: `--search-mode semantic --similarity-threshold 0.75`

3. **Hybrid Mode** (recommended):
   - First: Exact matches (score = 1.0)
   - Then: Semantic matches above threshold
   - Deduplicate by position
   - Use: `--search-mode hybrid`

**Database Storage**:
```python
class KeywordMatch:
    # ... existing fields ...
    match_score: float  # 1.0 for exact, 0.0-1.0 for semantic
    embedding: Optional[bytes]  # Pickled numpy array (optional)
```

**Performance Considerations**:
- Model loading: ~1 second (cached after first use)
- Encoding: ~10ms per sentence
- For 100 comments: ~1 second total
- Batch encoding for efficiency

**CLI Examples**:
```bash
# Find exact phrase
redditsearch search --keywords "pay for" --search-mode exact

# Find semantic variations (looser)
redditsearch search --keywords "pay for" --search-mode semantic --similarity-threshold 0.7

# Find semantic variations (stricter)
redditsearch search --keywords "pay for" --search-mode semantic --similarity-threshold 0.85

# Best of both worlds
redditsearch search --keywords "pay for,need a tool" --search-mode hybrid
```

**Model Choice**:
- Default: `all-MiniLM-L6-v2` (80MB, fast, good quality)
- Alternative: `all-mpnet-base-v2` (420MB, slower, best quality)
- Configurable in settings

### 2. Plugin Architecture for Multi-Source Support

**Purpose**: Allow searching across multiple platforms (Reddit, Twitter, HackerNews, Discord, etc.) with a unified interface.

**Design Pattern**: Plugin-based architecture with abstract base classes.

**Base Interface** (`src/sources/base.py`):
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class SourcePost:
    """Unified post representation across all sources"""
    source: str  # 'reddit', 'twitter', 'hackernews', etc.
    source_id: str  # Platform-specific ID
    title: Optional[str]
    body: str
    author: str
    source_location: str  # Subreddit, hashtag, category
    url: str
    score: int
    reply_count: int
    created_utc: datetime
    raw_data: Dict  # Original API response for debugging

@dataclass
class SourceReply:
    """Unified reply representation across all sources"""
    source: str
    source_id: str
    post_id: str  # Reference to parent post
    parent_id: Optional[str]  # For threading
    body: str
    author: str
    score: int
    depth: int
    created_utc: datetime
    raw_data: Dict

class DataSourcePlugin(ABC):
    """Abstract base class for all data source plugins"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier for this source (e.g., 'reddit')"""
        pass

    @abstractmethod
    def authenticate(self, credentials: Dict) -> bool:
        """Authenticate with the platform API"""
        pass

    @abstractmethod
    def search(
        self,
        keywords: List[str],
        targets: List[str],  # Subreddits, hashtags, etc.
        time_filter: str,
        min_score: int,
        max_results: int,
        search_mode: str = 'hybrid'
    ) -> List[SourcePost]:
        """Search for posts matching criteria"""
        pass

    @abstractmethod
    def get_replies(
        self,
        post: SourcePost,
        max_depth: int = 10
    ) -> List[SourceReply]:
        """Get replies/comments for a post"""
        pass

    @abstractmethod
    def get_rate_limits(self) -> Dict:
        """Return current rate limit status"""
        pass
```

**Reddit Plugin Implementation** (`src/sources/reddit/client.py`):
```python
import praw
from src.sources.base import DataSourcePlugin, SourcePost, SourceReply

class RedditPlugin(DataSourcePlugin):
    """Reddit data source implementation"""

    @property
    def source_name(self) -> str:
        return 'reddit'

    def authenticate(self, credentials: Dict) -> bool:
        self.reddit = praw.Reddit(
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            user_agent=credentials['user_agent']
        )
        return True

    def search(self, keywords, targets, time_filter, min_score, max_results, search_mode='hybrid'):
        posts = []
        for subreddit_name in targets:
            subreddit = self.reddit.subreddit(subreddit_name)
            # Search logic...
            for submission in subreddit.search(...):
                posts.append(SourcePost(
                    source='reddit',
                    source_id=submission.id,
                    title=submission.title,
                    body=submission.selftext,
                    author=submission.author.name,
                    source_location=f'r/{subreddit_name}',
                    url=submission.url,
                    score=submission.score,
                    reply_count=submission.num_comments,
                    created_utc=datetime.fromtimestamp(submission.created_utc),
                    raw_data={'submission': submission}
                ))
        return posts

    def get_replies(self, post, max_depth=10):
        # Traverse comment tree...
        pass
```

**Multi-Source Search Engine** (`src/core/search_engine.py`):
```python
from src.sources.base import DataSourcePlugin
from typing import List, Dict

class MultiSourceSearchEngine:
    """Orchestrate searches across multiple data sources"""

    def __init__(self):
        self.plugins: Dict[str, DataSourcePlugin] = {}

    def register_plugin(self, plugin: DataSourcePlugin):
        """Register a data source plugin"""
        self.plugins[plugin.source_name] = plugin

    def search(
        self,
        keywords: List[str],
        sources: Dict[str, List[str]],  # {'reddit': ['SaaS'], 'twitter': ['#startups']}
        **kwargs
    ):
        """Search across multiple sources in parallel"""
        all_posts = []

        for source_name, targets in sources.items():
            if source_name not in self.plugins:
                logger.warning(f"Source '{source_name}' not available")
                continue

            plugin = self.plugins[source_name]
            posts = plugin.search(keywords, targets, **kwargs)
            all_posts.extend(posts)

        return all_posts
```

**CLI Multi-Source Usage**:
```bash
# Search only Reddit (current behavior)
redditsearch search --keywords "pay for" --source reddit --targets "SaaS,Entrepreneur"

# Search only Twitter (future)
redditsearch search --keywords "pay for" --source twitter --targets "#startups,#SaaS"

# Search multiple sources simultaneously (future)
redditsearch search --keywords "pay for" \
  --source reddit --targets "SaaS,Entrepreneur" \
  --source twitter --targets "#startups" \
  --source hackernews --targets "Show HN"

# Combined visualization across all sources
redditsearch report <search_id>  # Shows Reddit + Twitter + HN data together
```

**Benefits**:
1. **Add new sources easily**: Implement `DataSourcePlugin` interface
2. **Source-agnostic analysis**: All analysis/visualization works with any source
3. **Unified storage**: Single database schema for all sources
4. **Combined insights**: Compare pain points across Reddit vs Twitter vs Discord
5. **Future-proof**: Support for future platforms without refactoring core

**Future Sources**:
- **Twitter/X**: Search tweets and replies (using Twitter API v2)
- **HackerNews**: Search via Algolia HN API
- **Discord**: Search public servers (with permissions)
- **Indie Hackers**: Forum discussions
- **Product Hunt**: Product comments
- **Stack Overflow**: Questions/answers in specific tags

**Implementation Priority**:
- Phase 3: Implement Reddit plugin (current focus)
- Future: Add plugin architecture with Reddit as first implementation
- Future: Add Twitter, HackerNews plugins as needed

### 3. Reddit API Setup
**User must obtain** (from https://www.reddit.com/prefs/apps):
- Application name
- Client ID
- Client secret

**Add to `.env`**:
```
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=reddit-customer-dev:v0.1.0 (by /u/USERNAME)
```

### 2. Deduplication Logic
**In `repositories.py`**:
```python
def get_or_create_submission(self, praw_submission, search_id):
    existing = session.query(Submission).filter_by(
        reddit_id=praw_submission.id
    ).first()

    if existing:
        existing.seen_count += 1
        return existing, False  # Not new
    else:
        new_sub = Submission.from_praw(praw_submission, search_id)
        new_sub.first_seen_search_id = search_id
        session.add(new_sub)
        return new_sub, True  # New
```

### 3. Comment Tree Traversal
**Handle multi-level threads**:
```python
def extract_comments(submission, keyword_patterns):
    # Replace MoreComments objects (limit to avoid rate limits)
    submission.comments.replace_more(limit=32)

    # Flatten comment tree
    for comment in submission.comments.list():
        if hasattr(comment, 'body'):  # Skip deleted
            # Check for keyword matches
            # Extract context (full paragraph)
            # Save to database
```

### 4. Keyword Context Extraction
**For each keyword match**:
```python
def extract_context(text, keyword, context_size=200):
    # Find keyword position
    match_start = text.lower().find(keyword.lower())

    # Get surrounding text
    context_before = text[max(0, match_start - context_size):match_start]
    matched_text = text[match_start:match_start + len(keyword)]
    context_after = text[match_start + len(keyword):match_start + len(keyword) + context_size]

    # Get full paragraph (split by \n\n or sentences)
    full_paragraph = extract_paragraph_containing_position(text, match_start)

    return KeywordMatch(
        keyword=keyword,
        context_before=context_before,
        matched_text=matched_text,
        context_after=context_after,
        full_paragraph=full_paragraph
    )
```

### 5. Default Subreddit Recommendations
**Seed `config/subreddits.yaml` with**:
- **Entrepreneurship**: SaaS, Entrepreneur, startups, smallbusiness, Bootstrapped, EntrepreneurRideAlong, SideProject
- **Product Development**: ProductManagement, userexperience, webdev
- **Business Ideas**: SomebodyMakeThis, AppIdeas, Lightbulb

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Can search Reddit with configurable keywords and subreddits
- ✅ Scrapes posts and comments with rate limiting
- ✅ Stores data in SQLite with deduplication
- ✅ Resumes interrupted searches
- ✅ Generates HTML dashboard with basic charts
- ✅ Performs keyword frequency and sentiment analysis

### Full Feature Set
- ✅ All 4 analysis types working (frequency, clustering, sentiment, context)
- ✅ Interactive Plotly visualizations
- ✅ CLI with all commands (search, report, list, resume, config)
- ✅ Comprehensive error handling
- ✅ Complete documentation

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Reddit API approval delay | High | Implement first, test when credentials arrive |
| Rate limiting too strict | Medium | Conservative approach, state management for resume |
| Transformer models too large | Medium | Use DistilBERT or lighter alternatives |
| Comment trees too deep | Medium | Limit depth, use `replace_more(limit=32)` |
| Data volume exceeds SQLite capacity | Low | SQLite handles millions of rows; optimize with indexes |

## Next Steps (When Implementation Begins)

1. **Setup**: Update `pyproject.toml`, create project structure
2. **Config**: Implement settings, create `.env.example`
3. **Database**: Define SQLAlchemy models, setup migrations
4. **Reddit Client**: Build PRAW wrapper with rate limiting
5. **CLI**: Create basic Click commands
6. **Search**: Implement core search logic
7. **Analysis**: Add analysis modules one by one
8. **Viz**: Build dashboard generator
9. **Test**: Manual testing with real Reddit data
10. **Polish**: Documentation, error handling, examples

## Questions for User Before Implementation

1. **Reddit credentials**: Have you received your app approval yet? (Need client_id, client_secret)
2. **Search scope**: Any specific subreddits you want to prioritize testing with?
3. **Keywords**: Do you have a starter list of pain point keywords beyond "pay for", "wish there was"?
4. **Output location**: Where do you want HTML reports saved? (default: `output/reports/`)
5. **Topic clustering**: How many topic clusters do you want (default: 5)?

---

## Files to Create/Modify

**Configuration**:
- `pyproject.toml` - Add all dependencies
- `.env.example` - Credential template
- `config/settings.py` - Pydantic settings
- `config/subreddits.yaml` - Default subreddit lists

**Core Application**:
- `main.py` - CLI entry point
- `src/storage/models.py` - Database models
- `src/scraper/reddit_client.py` - PRAW wrapper
- `src/scraper/rate_limiter.py` - Rate limiting
- `src/cli/commands.py` - CLI commands

**Analysis & Visualization**:
- `src/analysis/keyword_analyzer.py`
- `src/analysis/topic_clusterer.py`
- `src/analysis/sentiment_analyzer.py`
- `src/analysis/context_extractor.py`
- `src/visualization/dashboard.py`
- `src/visualization/charts.py`
- `src/visualization/templates/report.html`

**Documentation**:
- `README.md` - Update with usage guide
- `CLAUDE.md` - Update with architecture details
