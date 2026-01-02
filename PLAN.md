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
│   │   ├── context_extractor.py    # Context extraction
│   │   └── payment_signal_analyzer.py  # Payment willingness detection
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
- `sqlite-vec>=0.1.0` - Vector similarity search for SQLite

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

**Implementation** (`src/core/rate_limiter.py`):
```python
from datetime import timedelta
import time

class AdaptiveRateLimiter:
    """Adaptive rate limiter with time estimation"""

    def __init__(self, initial_delay: float = 2.0):
        self.current_delay = initial_delay
        self.success_count = 0
        self.last_request_time = 0

    def wait(self):
        """Wait before next request"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.current_delay:
            time.sleep(self.current_delay - elapsed)
        self.last_request_time = time.time()

    def on_success(self):
        """Gradually speed up after consecutive successes"""
        self.success_count += 1
        if self.success_count >= 10:
            self.current_delay *= 0.9  # Speed up by 10%
            self.success_count = 0

    def on_rate_limit(self, retry_after: int = None):
        """Exponential backoff on rate limit"""
        if retry_after:
            self.current_delay = retry_after
        else:
            self.current_delay = min(self.current_delay * 2, 60)
        self.success_count = 0

    def get_estimated_time_remaining(self, requests_remaining: int) -> timedelta:
        """
        Estimate how long remaining requests will take

        Args:
            requests_remaining: Number of API requests left to make

        Returns:
            timedelta: Estimated time to completion

        Example:
            >>> limiter = AdaptiveRateLimiter(current_delay=2.0)
            >>> limiter.get_estimated_time_remaining(100)
            timedelta(seconds=200)  # 100 requests * 2.0 seconds
        """
        return timedelta(seconds=requests_remaining * self.current_delay)

    def format_eta(self, requests_remaining: int) -> str:
        """
        Human-readable ETA string

        Returns:
            String like "3m 20s" or "1h 15m"
        """
        eta = self.get_estimated_time_remaining(requests_remaining)
        total_seconds = int(eta.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
```

**Progress Tracking Integration**:
- Use with Rich progress bars to show ETA
- Update estimate as rate limiter adapts (speeds up or slows down)
- Display in CLI: "Processing: 47/150 posts (ETA: 3m 45s)"

### CLI Commands and Dry Run

**Dry Run Feature**:

Add `--dry-run` flag to preview search scope and estimate time/resources before execution.

**Implementation** (`src/cli/commands.py`):
```python
@click.command()
@click.option('--keywords', required=True)
@click.option('--subreddits', required=True)
@click.option('--days', default=30)
@click.option('--min-score', default=5)
@click.option('--max-posts', default=100)
@click.option('--dry-run', is_flag=True, help='Preview search scope without executing')
def search(keywords, subreddits, days, min_score, max_posts, dry_run):
    """Search Reddit for keywords"""

    if dry_run:
        # Estimate search scope
        subreddit_list = subreddits.split(',')
        keyword_list = keywords.split(',')

        # Quick API call to estimate post counts (doesn't fetch full data)
        estimated_posts = estimate_post_count(subreddit_list, days, min_score)
        estimated_posts = min(estimated_posts, max_posts)

        # Estimate comment count (average ~15 comments per post)
        estimated_comments = estimated_posts * 15

        # Estimate API requests
        # 1 request per subreddit search + 1 per post for comments
        estimated_requests = len(subreddit_list) + estimated_posts

        # Calculate time estimate
        rate_limiter = AdaptiveRateLimiter()
        eta = rate_limiter.format_eta(estimated_requests)

        # Display preview
        console = Console()
        console.print("\n[bold cyan]Search Preview (Dry Run)[/bold cyan]\n")
        console.print(f"Keywords: {len(keyword_list)} ({', '.join(keyword_list)})")
        console.print(f"Subreddits: {len(subreddit_list)} ({', '.join(subreddit_list)})")
        console.print(f"Time window: Last {days} days")
        console.print(f"Minimum score: {min_score}")
        console.print(f"\n[bold]Estimated Scope:[/bold]")
        console.print(f"  • Posts to fetch: ~{estimated_posts}")
        console.print(f"  • Comments to scan: ~{estimated_comments:,}")
        console.print(f"  • API requests: ~{estimated_requests}")
        console.print(f"  • Estimated time: ~{eta}")
        console.print(f"\n[dim]Run without --dry-run to execute search[/dim]\n")
        return

    # Normal search execution...
    run_search(keywords, subreddits, days, min_score, max_posts)
```

**Helper Function** (`src/cli/validators.py`):
```python
def estimate_post_count(subreddits: List[str], days: int, min_score: int) -> int:
    """
    Quickly estimate how many posts will be fetched

    Uses Reddit API to get counts without fetching full data.
    Lightweight query that doesn't consume significant rate limit.
    """
    reddit = get_reddit_client()
    total = 0

    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            # Quick count query (doesn't fetch full posts)
            # Search last N days with score filter
            count = sum(1 for _ in subreddit.new(limit=100)
                       if is_within_days(_, days) and _.score >= min_score)
            total += count
        except Exception as e:
            # If can't estimate, use conservative default
            total += 50

    return total
```

**Primary Commands**:

```bash
# Preview search scope before executing (dry run)
redditsearch search \
  --keywords "pay for,wish there was,need a tool" \
  --subreddits "SaaS,Entrepreneur,startups" \
  --days 30 \
  --min-score 5 \
  --max-posts 100 \
  --dry-run

# Output:
# Search Preview (Dry Run)
#
# Keywords: 3 (pay for, wish there was, need a tool)
# Subreddits: 3 (SaaS, Entrepreneur, startups)
# Time window: Last 30 days
# Minimum score: 5
#
# Estimated Scope:
#   • Posts to fetch: ~247
#   • Comments to scan: ~3,705
#   • API requests: ~250
#   • Estimated time: ~8m 20s
#
# Run without --dry-run to execute search

# Use a preset (easiest method)
redditsearch search --preset saas_pain_points

# Use preset with overrides
redditsearch search --preset saas_pain_points --days 60 --max-posts 200

# List all available presets
redditsearch presets list

# Show details of a specific preset
redditsearch presets show saas_pain_points

# Search Reddit with manual parameters (exact keyword matching)
redditsearch search \
  --keywords "pay for,wish there was,need a tool" \
  --subreddits "SaaS,Entrepreneur,startups" \
  --days 30 \
  --min-score 5 \
  --max-posts 100

# Use a subreddit group instead of listing individual subreddits
redditsearch search \
  --keywords "pay for" \
  --group entrepreneurship \
  --days 30

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

**Preset Usage Examples**:

```bash
# Quick customer development - find SaaS opportunities
redditsearch search --preset saas_pain_points

# B2B opportunity hunting
redditsearch search --preset b2b_opportunities

# Find what developers are frustrated with
redditsearch search --preset developer_tools

# High-urgency needs (strong buying signals)
redditsearch search --preset urgent_needs

# Competitive intelligence gathering
redditsearch search --preset competitive_intel

# Productivity tool opportunities
redditsearch search --preset productivity_pain

# Feature gap analysis
redditsearch search --preset feature_gaps

# Combine preset with custom overrides
redditsearch search --preset saas_pain_points \
  --days 90 \
  --max-posts 500 \
  --comment-depth 10

# Preview preset before running
redditsearch search --preset b2b_opportunities --dry-run
```

### Analysis Pipeline

**Five Analysis Types**:

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
   - **Default mode**: Use pre-trained transformer model `cardiffnlp/twitter-roberta-base-sentiment-latest`
   - **Lite mode** (`--lite` flag): Use VADER (Valence Aware Dictionary and sEntiment Reasoner) for low-memory systems
   - Analyze full paragraph context
   - Aggregate by keyword
   - Extract high-negative examples (strong pain points)
   - **Resource considerations**: Transformer models require ~500MB RAM, VADER requires <10MB

4. **Payment Signal Detection** (`payment_signal_analyzer.py`) - **Critical for Solopreneurs**
   - Detect willingness to pay ("would pay $X", "shut up and take my money")
   - Extract current payment patterns ("currently paying $X/month")
   - Identify urgency signals ("desperately need", "need this now")
   - Price point extraction and analysis (min, max, median, avg)
   - Competitive intelligence (what competitors charge)
   - Social proof weighting (upvote scores validate demand)

5. **Context Extraction** (`context_extractor.py`)
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

**Reddit Source Configuration** (`config/sources/reddit.yaml`):
```yaml
# Subreddit groups for easy targeting
groups:
  entrepreneurship:
    - SaaS
    - Entrepreneur
    - startups
    - smallbusiness
    - Bootstrapped
    - EntrepreneurRideAlong
    - SideProject

  product_development:
    - ProductManagement
    - userexperience
    - webdev
    - SomebodyMakeThis
    - AppIdeas
    - Lightbulb

  b2b_business:
    - smallbusiness
    - Accounting
    - sales
    - marketing
    - freelance
    - consulting

  technical:
    - programming
    - webdev
    - selfhosted
    - sysadmin
    - devops

# Pre-configured search presets for common use cases
presets:
  # Find SaaS pain points people are willing to pay for
  saas_pain_points:
    subreddits: [SaaS, Entrepreneur, startups]
    keywords: ["pay for", "wish there was", "struggling with", "need a tool"]
    search_mode: hybrid
    days: 30
    min_score: 5
    comment_depth: 32
    description: "Find SaaS opportunities with payment signals"

  # Identify B2B software opportunities
  b2b_opportunities:
    subreddits: [smallbusiness, Accounting, sales, marketing]
    keywords: ["need software", "looking for tool", "manual process", "spreadsheet hell", "automate"]
    search_mode: hybrid
    days: 60
    min_score: 3
    comment_depth: 32
    description: "B2B workflow automation opportunities"

  # Find developer tool gaps
  developer_tools:
    subreddits: [programming, webdev, selfhosted, devops]
    keywords: ["wish there was", "missing feature", "need a better", "frustrated with"]
    search_mode: hybrid
    days: 45
    min_score: 10
    comment_depth: 10
    description: "Developer tooling pain points"

  # Validate product ideas with urgency signals
  urgent_needs:
    subreddits: [Entrepreneur, startups, SaaS, smallbusiness]
    keywords: ["desperately need", "urgently need", "can't find", "doesn't exist"]
    search_mode: hybrid
    days: 30
    min_score: 5
    comment_depth: 32
    description: "High-urgency unmet needs"

  # Find competitive intelligence (what people currently pay for)
  competitive_intel:
    subreddits: [SaaS, Entrepreneur, smallbusiness]
    keywords: ["currently paying", "subscription costs", "switched from", "using [Tool]"]
    search_mode: hybrid
    days: 90
    min_score: 3
    comment_depth: 20
    description: "Competitive pricing and switching behavior"

  # Discover productivity pain points
  productivity_pain:
    subreddits: [productivity, Entrepreneur, smallbusiness, freelance]
    keywords: ["waste time", "manually doing", "takes hours", "inefficient"]
    search_mode: hybrid
    days: 30
    min_score: 5
    comment_depth: 32
    description: "Productivity and efficiency problems"

  # Find feature requests and gaps
  feature_gaps:
    subreddits: [SaaS, ProductManagement, userexperience]
    keywords: ["missing feature", "would love if", "should have", "needs to add"]
    search_mode: semantic
    similarity_threshold: 0.75
    days: 60
    min_score: 5
    comment_depth: 20
    description: "Feature requests and product gaps"
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
- Create `config/sources/reddit.yaml` with subreddit groups and search presets
- Create `config/preset_loader.py` with PresetLoader class
- Create `.env.example` template
- Setup `src/` package structure (with `__init__.py` files)
- Implement `src/utils/logger.py`
- Create `tests/test_config.py` - Test settings loading, YAML parsing, and preset loading
- Create `pytest.ini` - Pytest configuration

**Testing**:
- Test that settings load correctly from .env
- Test YAML config parsing (groups and presets)
- Test PresetLoader functionality (get_preset, list_presets, get_group, apply_preset)
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
- `src/analysis/payment_signal_analyzer.py` - Payment willingness detection (critical for solopreneurs)
- `src/analysis/context_extractor.py` - Extract and rank contexts
- `tests/test_analysis.py` - Test all analysis modules

**Testing**:
- Test keyword frequency calculations
- Test co-occurrence matrix generation
- Test topic clustering with sample data
- Test sentiment analysis with known examples
- Test payment signal detection with known phrases
- Test amount extraction from various formats ($50, $50/mo, 50 dollars per month)
- Test frequency detection (monthly, yearly, one-time)
- Test payment signal aggregation and statistics
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

**Similarity Threshold Guidance**:

Understanding the tradeoff between precision and recall:

| Threshold | Quality | Use Case | Example Matches for "pay for" |
|-----------|---------|----------|--------------------------------|
| **0.85+** | Very Strict | Almost synonyms only, high precision | "willing to pay", "would pay for" |
| **0.75-0.85** | Recommended | Semantically similar, balanced | "spend money on", "invest in", "worth paying" |
| **0.65-0.75** | Loose | Broader concepts, higher recall | "budget for", "afford", "financial commitment" |
| **<0.65** | Too Noisy | Not recommended, low precision | Unrelated financial terms, noise |

**Recommendation**: Start with **0.75** (default) for hybrid mode. Adjust based on results:
- Getting too many irrelevant matches? Increase to 0.80-0.85
- Missing relevant variations? Decrease to 0.70-0.75
- For customer development, **0.75** balances finding variations while avoiding noise

**Testing Your Threshold**:
```bash
# Test with strict threshold (high precision)
redditsearch search --keywords "pay for" --search-mode semantic --similarity-threshold 0.85 --max-posts 20

# Test with recommended threshold (balanced)
redditsearch search --keywords "pay for" --search-mode semantic --similarity-threshold 0.75 --max-posts 20

# Test with loose threshold (high recall)
redditsearch search --keywords "pay for" --search-mode semantic --similarity-threshold 0.70 --max-posts 20

# Compare results to find your sweet spot
```

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

### 3. Payment Signal Analyzer

**Purpose**: Detect explicit payment willingness signals to validate business opportunities. This is critical for solopreneurship - finding pain points people will actually pay to solve.

**Why This Matters**:
- Distinguishes between complaints and actual market demand
- Provides price point validation ("would pay $50/month")
- Identifies competitive pricing ("currently paying $X for Y")
- Quantifies market urgency (e.g., "desperately need", "would immediately buy")

**Implementation** (`src/analysis/payment_signal_analyzer.py`):

```python
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class PaymentSignal:
    """Detected payment willingness signal"""
    text: str
    signal_type: str  # 'willingness', 'current_payment', 'price_mention', 'urgency'
    amount: Optional[float]  # Extracted dollar amount if present
    currency: str  # 'USD', 'EUR', etc.
    frequency: Optional[str]  # 'monthly', 'yearly', 'one-time', etc.
    context: str  # Full surrounding context
    source: str  # Post/comment ID
    score: int  # Upvotes (social proof)
    confidence: float  # 0.0-1.0 confidence in detection

class PaymentSignalAnalyzer:
    """Detect and analyze payment willingness signals"""

    def __init__(self):
        # Payment willingness patterns
        self.willingness_patterns = [
            r"would pay \$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"willing to pay \$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"shut up and take my money",
            r"i(?:'d| would) buy (?:this|that|it)",
            r"worth \$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"happily pay \$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"throw money at (?:this|you)",
        ]

        # Current payment patterns (competitive intel)
        self.current_payment_patterns = [
            r"(?:currently|already) paying \$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"pay(?:ing)? \$?(\d+(?:,\d{3})*(?:\.\d{2})?) (?:per|a|\/)\s*(month|year|mo|yr)",
            r"costs? (?:me|us) \$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"subscription (?:is|costs?) \$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
        ]

        # Price point mentions
        self.price_mention_patterns = [
            r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)(?:/|\s+per\s+)(month|year|mo|yr)",
            r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s+dollars?\s+(?:per|a)\s+(month|year)",
        ]

        # Urgency indicators (high buying intent)
        self.urgency_patterns = [
            r"desperately need",
            r"urgently need",
            r"need (?:this|it) (?:now|asap|immediately|yesterday)",
            r"can't wait for",
            r"where do i sign up",
            r"take my money",
        ]

        # Frequency mapping
        self.frequency_map = {
            'month': 'monthly',
            'mo': 'monthly',
            'year': 'yearly',
            'yr': 'yearly',
            'annual': 'yearly',
            'one-time': 'one-time',
            'once': 'one-time',
        }

    def analyze(self, keyword_matches: List[Dict]) -> Dict:
        """
        Analyze keyword matches for payment signals

        Args:
            keyword_matches: List of keyword match records from database

        Returns:
            Dictionary with payment signal analysis
        """
        signals = []

        for match in keyword_matches:
            text = match['full_paragraph'].lower()

            # Detect willingness to pay
            for pattern in self.willingness_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    amount = self._extract_amount(text, pattern)
                    frequency = self._extract_frequency(text)
                    signals.append(PaymentSignal(
                        text=match['full_paragraph'],
                        signal_type='willingness',
                        amount=amount,
                        currency='USD',  # TODO: Multi-currency support
                        frequency=frequency,
                        context=match['full_paragraph'],
                        source=match['post_id'] or match['reply_id'],
                        score=match.get('score', 0),
                        confidence=0.9 if amount else 0.7
                    ))

            # Detect current payments (competitive intel)
            for pattern in self.current_payment_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    amount = self._extract_amount(text, pattern)
                    frequency = self._extract_frequency(text)
                    signals.append(PaymentSignal(
                        text=match['full_paragraph'],
                        signal_type='current_payment',
                        amount=amount,
                        currency='USD',
                        frequency=frequency,
                        context=match['full_paragraph'],
                        source=match['post_id'] or match['reply_id'],
                        score=match.get('score', 0),
                        confidence=0.95 if amount else 0.6
                    ))

            # Detect urgency signals
            for pattern in self.urgency_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    signals.append(PaymentSignal(
                        text=match['full_paragraph'],
                        signal_type='urgency',
                        amount=None,
                        currency='USD',
                        frequency=None,
                        context=match['full_paragraph'],
                        source=match['post_id'] or match['reply_id'],
                        score=match.get('score', 0),
                        confidence=0.8
                    ))

        return self._aggregate_signals(signals)

    def _extract_amount(self, text: str, pattern: str) -> Optional[float]:
        """Extract dollar amount from text using pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.groups():
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                return None
        return None

    def _extract_frequency(self, text: str) -> Optional[str]:
        """Extract payment frequency from text"""
        for key, value in self.frequency_map.items():
            if re.search(rf'\b{key}\b', text, re.IGNORECASE):
                return value
        return None

    def _aggregate_signals(self, signals: List[PaymentSignal]) -> Dict:
        """Aggregate payment signals into summary statistics"""

        # Group by signal type
        by_type = defaultdict(list)
        for signal in signals:
            by_type[signal.signal_type].append(signal)

        # Extract price points
        price_points = [s.amount for s in signals if s.amount is not None]
        monthly_prices = [
            s.amount for s in signals
            if s.amount and s.frequency == 'monthly'
        ]

        # Sort by social proof (score)
        top_signals = sorted(
            signals,
            key=lambda s: (s.confidence * s.score),
            reverse=True
        )[:20]

        return {
            'total_signals': len(signals),
            'by_type': {
                'willingness': len(by_type['willingness']),
                'current_payment': len(by_type['current_payment']),
                'urgency': len(by_type['urgency']),
            },
            'price_analysis': {
                'mentions': len(price_points),
                'min': min(price_points) if price_points else None,
                'max': max(price_points) if price_points else None,
                'median': self._median(price_points) if price_points else None,
                'avg': sum(price_points) / len(price_points) if price_points else None,
                'monthly_avg': sum(monthly_prices) / len(monthly_prices) if monthly_prices else None,
            },
            'top_signals': [
                {
                    'type': s.signal_type,
                    'amount': s.amount,
                    'frequency': s.frequency,
                    'text': s.text[:200] + '...' if len(s.text) > 200 else s.text,
                    'score': s.score,
                    'confidence': s.confidence,
                }
                for s in top_signals
            ],
            'competitive_intel': [
                {
                    'amount': s.amount,
                    'frequency': s.frequency,
                    'text': s.text[:200] + '...' if len(s.text) > 200 else s.text,
                    'score': s.score,
                }
                for s in by_type['current_payment']
                if s.amount is not None
            ],
        }

    @staticmethod
    def _median(values: List[float]) -> float:
        """Calculate median of list"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_values[mid - 1] + sorted_values[mid]) / 2
        return sorted_values[mid]
```

**Example Output**:

```json
{
  "total_signals": 47,
  "by_type": {
    "willingness": 23,
    "current_payment": 15,
    "urgency": 9
  },
  "price_analysis": {
    "mentions": 18,
    "min": 9.99,
    "max": 199.0,
    "median": 49.0,
    "avg": 67.83,
    "monthly_avg": 52.45
  },
  "top_signals": [
    {
      "type": "willingness",
      "amount": 50.0,
      "frequency": "monthly",
      "text": "I would easily pay $50/month for a tool that automates this. Currently spending 10+ hours a week doing it manually.",
      "score": 247,
      "confidence": 0.9
    },
    {
      "type": "current_payment",
      "amount": 199.0,
      "frequency": "monthly",
      "text": "We're currently paying $199/mo for [Tool X] but it's missing critical features like...",
      "score": 183,
      "confidence": 0.95
    }
  ],
  "competitive_intel": [
    {
      "amount": 199.0,
      "frequency": "monthly",
      "text": "Currently using [Tool X] at $199/mo...",
      "score": 183
    }
  ]
}
```

**Dashboard Visualization**:

Add to `src/visualization/charts.py`:

```python
def create_payment_signal_chart(payment_data: Dict) -> go.Figure:
    """Create payment signal analysis chart"""

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Signal Types Distribution',
            'Price Point Distribution',
            'Top Payment Signals',
            'Competitive Pricing'
        ),
        specs=[[{'type': 'pie'}, {'type': 'histogram'}],
               [{'type': 'table'}, {'type': 'bar'}]]
    )

    # Signal types pie chart
    fig.add_trace(go.Pie(
        labels=list(payment_data['by_type'].keys()),
        values=list(payment_data['by_type'].values()),
        name='Signal Types'
    ), row=1, col=1)

    # Price distribution histogram
    if payment_data['top_signals']:
        prices = [s['amount'] for s in payment_data['top_signals'] if s['amount']]
        fig.add_trace(go.Histogram(
            x=prices,
            name='Price Points',
            nbinsx=10
        ), row=1, col=2)

    # Top signals table
    top_signals = payment_data['top_signals'][:10]
    fig.add_trace(go.Table(
        header=dict(values=['Amount', 'Freq', 'Score', 'Text']),
        cells=dict(values=[
            [f"${s['amount']:.2f}" if s['amount'] else 'N/A' for s in top_signals],
            [s['frequency'] or 'N/A' for s in top_signals],
            [s['score'] for s in top_signals],
            [s['text'][:50] + '...' for s in top_signals],
        ])
    ), row=2, col=1)

    # Competitive pricing
    competitive = payment_data['competitive_intel'][:10]
    if competitive:
        fig.add_trace(go.Bar(
            x=[c['amount'] for c in competitive],
            y=[f"Competitor {i+1}" for i in range(len(competitive))],
            orientation='h',
            name='Current Pricing'
        ), row=2, col=2)

    fig.update_layout(height=800, showlegend=False, title_text="Payment Signal Analysis")
    return fig
```

**Key Insights for Solopreneurs**:

1. **Willingness to Pay**: How many people explicitly said they'd pay?
2. **Price Points**: What's the median/average price people mention?
3. **Monthly Recurring**: Focus on MRR-generating opportunities
4. **Competitive Intel**: What are people currently paying for similar solutions?
5. **Urgency Signals**: High buying intent = faster validation
6. **Social Proof**: High-scored comments = validated demand

**Phase 5 Update**:
Add to testing:
- Test payment signal detection with known examples
- Test amount extraction from various formats ($50, $50/mo, 50 dollars per month)
- Test frequency detection (monthly, yearly, one-time)
- Test aggregation and statistics calculation

### 4. Preset Configuration System

**Purpose**: Simplify common customer development workflows with pre-configured search presets.

**Benefits**:
- **Quick start**: Users can run proven search patterns immediately
- **Best practices**: Encode optimal parameters for different use cases
- **Consistency**: Ensure searches follow validated approaches
- **Discoverability**: Help users learn what parameters work well together

**Implementation** (`src/cli/validators.py` or `src/config/preset_loader.py`):

```python
import yaml
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class SearchPreset:
    """Pre-configured search parameters"""
    name: str
    description: str
    subreddits: List[str]
    keywords: List[str]
    search_mode: str = 'hybrid'
    similarity_threshold: float = 0.75
    days: int = 30
    min_score: int = 5
    comment_depth: int = 32
    max_posts: Optional[int] = None

class PresetLoader:
    """Load and manage search presets from YAML config"""

    def __init__(self, config_path: str = 'config/sources/reddit.yaml'):
        self.config_path = Path(config_path)
        self._presets = {}
        self._groups = {}
        self._load_config()

    def _load_config(self):
        """Load presets and groups from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Load subreddit groups
        self._groups = config.get('groups', {})

        # Load presets
        for name, preset_config in config.get('presets', {}).items():
            self._presets[name] = SearchPreset(
                name=name,
                description=preset_config.get('description', ''),
                subreddits=preset_config['subreddits'],
                keywords=preset_config['keywords'],
                search_mode=preset_config.get('search_mode', 'hybrid'),
                similarity_threshold=preset_config.get('similarity_threshold', 0.75),
                days=preset_config.get('days', 30),
                min_score=preset_config.get('min_score', 5),
                comment_depth=preset_config.get('comment_depth', 32),
                max_posts=preset_config.get('max_posts', None)
            )

    def get_preset(self, name: str) -> SearchPreset:
        """Get a preset by name"""
        if name not in self._presets:
            available = ', '.join(self._presets.keys())
            raise ValueError(
                f"Preset '{name}' not found. Available presets: {available}"
            )
        return self._presets[name]

    def list_presets(self) -> List[Dict[str, str]]:
        """List all available presets with descriptions"""
        return [
            {
                'name': preset.name,
                'description': preset.description,
                'subreddits': len(preset.subreddits),
                'keywords': len(preset.keywords)
            }
            for preset in self._presets.values()
        ]

    def get_group(self, name: str) -> List[str]:
        """Get subreddit list for a group"""
        if name not in self._groups:
            available = ', '.join(self._groups.keys())
            raise ValueError(
                f"Group '{name}' not found. Available groups: {available}"
            )
        return self._groups[name]

    def apply_preset(self, preset: SearchPreset, overrides: Dict) -> Dict:
        """
        Apply preset with optional parameter overrides

        Args:
            preset: SearchPreset object
            overrides: Dict of parameters to override (from CLI flags)

        Returns:
            Dict of final search parameters
        """
        params = {
            'keywords': preset.keywords,
            'subreddits': preset.subreddits,
            'search_mode': preset.search_mode,
            'similarity_threshold': preset.similarity_threshold,
            'days': preset.days,
            'min_score': preset.min_score,
            'comment_depth': preset.comment_depth,
            'max_posts': preset.max_posts,
        }

        # Apply overrides from CLI
        for key, value in overrides.items():
            if value is not None:
                params[key] = value

        return params
```

**CLI Integration** (`src/cli/commands.py`):

```python
from src.config.preset_loader import PresetLoader

@click.command()
@click.option('--preset', type=str, help='Use a pre-configured search preset')
@click.option('--keywords', type=str, help='Keywords to search for (comma-separated)')
@click.option('--subreddits', type=str, help='Subreddits to search (comma-separated)')
@click.option('--group', type=str, help='Use a subreddit group from config')
@click.option('--days', type=int, help='Search posts from last N days')
@click.option('--min-score', type=int, help='Minimum post score')
@click.option('--comment-depth', type=int, help='Comment depth limit')
@click.option('--max-posts', type=int, help='Maximum posts to fetch')
@click.option('--search-mode', type=click.Choice(['exact', 'semantic', 'hybrid']))
@click.option('--similarity-threshold', type=float)
@click.option('--dry-run', is_flag=True)
def search(preset, keywords, subreddits, group, days, min_score, comment_depth,
           max_posts, search_mode, similarity_threshold, dry_run):
    """Search Reddit for customer development insights"""

    loader = PresetLoader()

    # If preset specified, load it
    if preset:
        preset_obj = loader.get_preset(preset)

        # Build overrides dict from CLI flags
        overrides = {
            'keywords': keywords.split(',') if keywords else None,
            'subreddits': subreddits.split(',') if subreddits else None,
            'days': days,
            'min_score': min_score,
            'comment_depth': comment_depth,
            'max_posts': max_posts,
            'search_mode': search_mode,
            'similarity_threshold': similarity_threshold,
        }

        # Apply preset with overrides
        params = loader.apply_preset(preset_obj, overrides)

        console.print(f"[cyan]Using preset:[/cyan] {preset_obj.name}")
        console.print(f"[dim]{preset_obj.description}[/dim]\n")

    # If group specified instead of individual subreddits
    elif group:
        subreddit_list = loader.get_group(group)
        params = {
            'keywords': keywords.split(','),
            'subreddits': subreddit_list,
            'days': days or 30,
            'min_score': min_score or 5,
            'comment_depth': comment_depth or 32,
            'max_posts': max_posts,
            'search_mode': search_mode or 'hybrid',
            'similarity_threshold': similarity_threshold or 0.75,
        }

    # Manual parameters
    else:
        if not keywords or not subreddits:
            raise click.UsageError(
                "Either --preset, or both --keywords and --subreddits/--group required"
            )

        params = {
            'keywords': keywords.split(','),
            'subreddits': subreddits.split(','),
            'days': days or 30,
            'min_score': min_score or 5,
            'comment_depth': comment_depth or 32,
            'max_posts': max_posts,
            'search_mode': search_mode or 'hybrid',
            'similarity_threshold': similarity_threshold or 0.75,
        }

    # Execute search or dry run
    if dry_run:
        display_dry_run_preview(params)
    else:
        execute_search(params)

@click.group()
def presets():
    """Manage search presets"""
    pass

@presets.command('list')
def list_presets():
    """List all available presets"""
    loader = PresetLoader()
    presets = loader.list_presets()

    console = Console()
    table = Table(title="Available Search Presets")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Subreddits", justify="right", style="green")
    table.add_column("Keywords", justify="right", style="green")

    for preset in presets:
        table.add_row(
            preset['name'],
            preset['description'],
            str(preset['subreddits']),
            str(preset['keywords'])
        )

    console.print(table)

@presets.command('show')
@click.argument('preset_name')
def show_preset(preset_name):
    """Show detailed configuration for a preset"""
    loader = PresetLoader()
    preset = loader.get_preset(preset_name)

    console = Console()
    console.print(f"\n[bold cyan]{preset.name}[/bold cyan]")
    console.print(f"[dim]{preset.description}[/dim]\n")
    console.print(f"[bold]Configuration:[/bold]")
    console.print(f"  • Keywords: {', '.join(preset.keywords)}")
    console.print(f"  • Subreddits: {', '.join(preset.subreddits)}")
    console.print(f"  • Search mode: {preset.search_mode}")
    console.print(f"  • Similarity threshold: {preset.similarity_threshold}")
    console.print(f"  • Time window: {preset.days} days")
    console.print(f"  • Minimum score: {preset.min_score}")
    console.print(f"  • Comment depth: {preset.comment_depth}")
    if preset.max_posts:
        console.print(f"  • Max posts: {preset.max_posts}")
    console.print()
```

**Usage Examples**:

```bash
# List all presets
$ redditsearch presets list

Available Search Presets
┌──────────────────────┬────────────────────────────────────────┬────────────┬──────────┐
│ Name                 │ Description                            │ Subreddits │ Keywords │
├──────────────────────┼────────────────────────────────────────┼────────────┼──────────┤
│ saas_pain_points     │ Find SaaS opportunities with payment   │          3 │        4 │
│                      │ signals                                │            │          │
│ b2b_opportunities    │ B2B workflow automation opportunities  │          4 │        5 │
│ developer_tools      │ Developer tooling pain points          │          4 │        4 │
│ urgent_needs         │ High-urgency unmet needs               │          4 │        4 │
│ competitive_intel    │ Competitive pricing and switching      │          3 │        4 │
│                      │ behavior                               │            │          │
│ productivity_pain    │ Productivity and efficiency problems   │          4 │        4 │
│ feature_gaps         │ Feature requests and product gaps      │          3 │        4 │
└──────────────────────┴────────────────────────────────────────┴────────────┴──────────┘

# Show preset details
$ redditsearch presets show saas_pain_points

saas_pain_points
Find SaaS opportunities with payment signals

Configuration:
  • Keywords: pay for, wish there was, struggling with, need a tool
  • Subreddits: SaaS, Entrepreneur, startups
  • Search mode: hybrid
  • Similarity threshold: 0.75
  �� Time window: 30 days
  • Minimum score: 5
  • Comment depth: 32

# Use preset directly
$ redditsearch search --preset saas_pain_points

Using preset: saas_pain_points
Find SaaS opportunities with payment signals

Searching 3 subreddits for 4 keywords...
...

# Override preset parameters
$ redditsearch search --preset saas_pain_points --days 90 --comment-depth 10

Using preset: saas_pain_points
Find SaaS opportunities with payment signals

Overrides applied:
  • Time window: 90 days (was 30)
  • Comment depth: 10 (was 32)

Searching 3 subreddits for 4 keywords...
```

**Benefits for Users**:

1. **Beginner-friendly**: New users can start immediately without learning all parameters
2. **Best practices**: Presets encode proven search strategies
3. **Discoverability**: `presets list` helps users learn what's possible
4. **Flexibility**: Can override any parameter while keeping preset defaults
5. **Documentation**: Each preset's description explains its purpose
6. **Validation**: Users can validate app ideas with proven search patterns

**Testing** (`tests/test_config.py`):
```python
def test_preset_loader():
    """Test preset loading from YAML"""
    loader = PresetLoader('config/sources/reddit.yaml')

    # Test getting preset
    preset = loader.get_preset('saas_pain_points')
    assert preset.name == 'saas_pain_points'
    assert 'pay for' in preset.keywords
    assert 'SaaS' in preset.subreddits

    # Test listing presets
    presets = loader.list_presets()
    assert len(presets) >= 7

    # Test apply with overrides
    params = loader.apply_preset(preset, {'days': 60})
    assert params['days'] == 60
    assert params['keywords'] == preset.keywords  # Not overridden

    # Test group loading
    group = loader.get_group('entrepreneurship')
    assert 'SaaS' in group
    assert 'Entrepreneur' in group
```

### 5. Lite Mode for Low-Memory Systems

**Purpose**: Provide a low-memory alternative for users on constrained systems (8GB RAM or less) by using lightweight NLP libraries instead of transformer models.

**Problem**:
- **Transformer models** (`cardiffnlp/twitter-roberta-base-sentiment-latest`) require ~500MB RAM minimum
- **Sentence transformers** (`all-MiniLM-L6-v2`) require ~80MB RAM for embeddings
- **Combined**: Running both simultaneously can require 600-800MB+ RAM
- **Impact**: On 8GB systems with other applications, this can cause swapping, crashes, or extreme slowness

**Solution**: Add `--lite` flag that switches to dictionary-based sentiment analysis

**Dependencies**:
```python
# pyproject.toml - Lite mode dependencies (always installed, lightweight)
- `vaderSentiment>=3.3.2` - Rule-based sentiment analysis (~2MB)

# Default mode dependencies (optional for lite users)
- `transformers>=4.36.0` - Sentiment analysis models (mark as optional)
- `torch>=2.1.0` - PyTorch (mark as optional)
```

**Implementation** (`src/analysis/sentiment_analyzer.py`):

```python
from typing import List, Dict, Optional
import logging

# Try to import transformer-based sentiment analyzer
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Use --lite flag for VADER sentiment analysis.")

# Always import VADER (lightweight, always available)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    """
    Sentiment analysis with automatic fallback

    Modes:
    - Default (transformers=True): Use RoBERTa transformer model (high accuracy, high memory)
    - Lite (transformers=False): Use VADER dictionary-based model (fast, low memory)
    """

    def __init__(self, use_transformers: bool = True):
        """
        Initialize sentiment analyzer

        Args:
            use_transformers: If True and available, use transformer models.
                             If False or unavailable, use VADER.
        """
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE

        if self.use_transformers:
            logging.info("Loading transformer-based sentiment analyzer (RoBERTa)...")
            try:
                self.model = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=-1  # CPU only (GPU would require even more memory)
                )
                logging.info("Transformer model loaded successfully (~500MB RAM)")
            except Exception as e:
                logging.warning(f"Failed to load transformer model: {e}")
                logging.info("Falling back to VADER sentiment analyzer...")
                self.use_transformers = False
                self.vader = SentimentIntensityAnalyzer()
        else:
            logging.info("Using VADER sentiment analyzer (lite mode, <10MB RAM)")
            self.vader = SentimentIntensityAnalyzer()

    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text

        Args:
            text: Input text to analyze

        Returns:
            Dict with sentiment scores:
            {
                'label': 'positive' | 'negative' | 'neutral',
                'score': 0.0-1.0 confidence,
                'compound': -1.0 to 1.0 (VADER only)
            }
        """
        if self.use_transformers:
            return self._analyze_transformer(text)
        else:
            return self._analyze_vader(text)

    def _analyze_transformer(self, text: str) -> Dict[str, float]:
        """Use transformer model for sentiment analysis"""
        # Truncate to model's max length (512 tokens for RoBERTa)
        # Approx 4 chars per token = ~2000 characters
        text = text[:2000]

        result = self.model(text)[0]

        # Normalize label names
        label_map = {
            'LABEL_0': 'negative',
            'LABEL_1': 'neutral',
            'LABEL_2': 'positive',
            'negative': 'negative',
            'neutral': 'neutral',
            'positive': 'positive'
        }

        return {
            'label': label_map.get(result['label'], result['label']),
            'score': result['score'],
            'compound': None  # Not available for transformers
        }

    def _analyze_vader(self, text: str) -> Dict[str, float]:
        """Use VADER for sentiment analysis (lite mode)"""
        scores = self.vader.polarity_scores(text)

        # VADER returns: {'neg': 0.0, 'neu': 0.5, 'pos': 0.5, 'compound': 0.5}
        # Compound score: -1 (most negative) to +1 (most positive)

        # Determine label based on compound score
        compound = scores['compound']
        if compound >= 0.05:
            label = 'positive'
            score = scores['pos']
        elif compound <= -0.05:
            label = 'negative'
            score = scores['neg']
        else:
            label = 'neutral'
            score = scores['neu']

        return {
            'label': label,
            'score': score,  # Confidence in this specific label
            'compound': compound  # Overall sentiment score
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment for multiple texts

        Args:
            texts: List of text strings

        Returns:
            List of sentiment dictionaries
        """
        if self.use_transformers:
            # Transformers support batch processing (more efficient)
            truncated = [t[:2000] for t in texts]
            results = self.model(truncated)

            return [
                {
                    'label': r['label'],
                    'score': r['score'],
                    'compound': None
                }
                for r in results
            ]
        else:
            # VADER processes one at a time (still fast)
            return [self.analyze_text(text) for text in texts]

    def get_mode_info(self) -> Dict[str, str]:
        """Return information about current sentiment analysis mode"""
        return {
            'mode': 'transformer' if self.use_transformers else 'vader',
            'model': 'cardiffnlp/twitter-roberta-base-sentiment-latest' if self.use_transformers else 'VADER',
            'memory_usage': '~500MB' if self.use_transformers else '<10MB',
            'speed': 'Slower (ML model)' if self.use_transformers else 'Faster (rule-based)'
        }
```

**CLI Integration** (`src/cli/commands.py`):

```python
@click.command()
@click.option('--preset', type=str, help='Use a pre-configured search preset')
@click.option('--keywords', type=str, help='Keywords to search for (comma-separated)')
@click.option('--subreddits', type=str, help='Subreddits to search (comma-separated)')
# ... other options ...
@click.option('--lite', is_flag=True, help='Use lite mode (low memory, dictionary-based sentiment analysis)')
def search(preset, keywords, subreddits, lite, **kwargs):
    """Search Reddit for customer development insights"""

    # Pass lite flag to analysis pipeline
    params = {
        # ... other params ...
        'lite_mode': lite
    }

    if lite:
        console.print("[yellow]⚡ Lite mode enabled[/yellow]")
        console.print("[dim]Using VADER sentiment analysis (<10MB RAM) instead of transformers[/dim]\n")

    execute_search(params)

@click.command()
@click.argument('search_id')
@click.option('--lite', is_flag=True, help='Use lite mode for analysis')
def report(search_id, lite):
    """Generate report for a completed search"""

    # Generate report with lite mode if requested
    generate_report(search_id, lite_mode=lite)
```

**Usage Examples**:

```bash
# Default mode (transformers, higher memory usage)
redditsearch search --preset saas_pain_points

# Lite mode (VADER, low memory usage)
redditsearch search --preset saas_pain_points --lite

# Generate report in lite mode (useful if you ran search without --lite but want low-memory analysis)
redditsearch report <search_id> --lite

# Dry run shows memory mode
redditsearch search --preset saas_pain_points --lite --dry-run
# Output:
# Search Preview (Dry Run)
# ...
# Analysis mode: Lite (VADER sentiment, <10MB RAM)
# ...
```

**Settings Configuration** (`config/settings.py`):

```python
class Settings(BaseSettings):
    # ... other settings ...

    # Sentiment analysis configuration
    SENTIMENT_USE_TRANSFORMERS: bool = True  # Default: use transformers if available
    SENTIMENT_LITE_MODE: bool = False  # Default: disabled

    # Override via environment variable or CLI flag
    # CLI flag takes precedence over env variable
```

**Performance Comparison**:

| Metric | Default Mode (Transformers) | Lite Mode (VADER) |
|--------|----------------------------|-------------------|
| **Memory Usage** | ~500-800MB | <10MB |
| **Model Load Time** | ~5-10 seconds | <1 second |
| **Processing Speed** | ~50-100 texts/sec | ~1000+ texts/sec |
| **Accuracy** | Higher (ML-based) | Good (rule-based) |
| **GPU Support** | Yes (optional) | No (CPU only) |
| **Best For** | High accuracy, ample RAM | Low memory, speed |

**Accuracy Comparison**:

For customer development use cases, VADER performs surprisingly well:

- **Positive pain points**: "I would love a tool that..." → Both detect as positive
- **Frustration**: "This is so annoying and frustrating" → Both detect as negative
- **Neutral observations**: "Currently using Tool X" → Both detect as neutral
- **Complex sentiment**: "Love the idea but hate the execution" → Transformers slightly better

**For most solopreneur customer development**, VADER's accuracy is sufficient because:
1. We're looking for strong signals (frustration, excitement)
2. We aggregate across many comments (individual errors average out)
3. We combine with other signals (payment willingness, urgency)

**Testing**:

```python
def test_sentiment_analyzer_modes():
    """Test both transformer and VADER modes"""

    # Test transformer mode (if available)
    analyzer_transformer = SentimentAnalyzer(use_transformers=True)
    result_t = analyzer_transformer.analyze_text("I would love to pay for this!")
    assert result_t['label'] == 'positive'

    # Test VADER mode
    analyzer_vader = SentimentAnalyzer(use_transformers=False)
    result_v = analyzer_vader.analyze_text("I would love to pay for this!")
    assert result_v['label'] == 'positive'
    assert result_v['compound'] > 0  # VADER provides compound score

    # Test mode info
    info_vader = analyzer_vader.get_mode_info()
    assert info_vader['mode'] == 'vader'
    assert info_vader['memory_usage'] == '<10MB'
```

**User Communication**:

When lite mode is active, show clear indicators:

```
$ redditsearch search --preset saas_pain_points --lite

⚡ Lite mode enabled
Using VADER sentiment analysis (<10MB RAM) instead of transformers

Using preset: saas_pain_points
Find SaaS opportunities with payment signals

Searching 3 subreddits for 4 keywords...

Analysis Pipeline:
  ✓ Keyword frequency analysis
  ✓ Topic clustering (scikit-learn)
  ⚡ Sentiment analysis (VADER - lite mode)
  ✓ Payment signal detection
  ✓ Context extraction

[Progress continues...]
```

**When to Recommend Lite Mode**:

Add to README.md:

```markdown
### Lite Mode (Low Memory)

If you're on a system with 8GB RAM or less, or experiencing memory issues, use `--lite`:

```bash
# Use lite mode for searches
redditsearch search --preset saas_pain_points --lite

# Use lite mode for report generation
redditsearch report <search_id> --lite
```

**Lite mode differences**:
- ✅ Uses VADER sentiment analysis instead of transformer models
- ✅ Reduces memory usage from ~800MB to <100MB total
- ✅ 10-20x faster sentiment processing
- ✅ Still provides accurate sentiment for customer development
- ⚠️ Slightly lower accuracy on complex/ambiguous sentiment
```

**Phase 5 Update**:
Add to testing requirements:
- Test sentiment analyzer with both transformer and VADER modes
- Test automatic fallback when transformers unavailable
- Test --lite flag in CLI
- Verify memory usage difference between modes

**Dependencies Update** (`pyproject.toml`):

```toml
[project]
name = "redditsearch"
dependencies = [
    "praw>=7.7.1",
    "sqlalchemy>=2.0.0",
    "click>=8.1.0",
    "rich>=13.7.0",
    # ... other core dependencies ...
    "vaderSentiment>=3.3.2",  # Always installed (lite mode)
    "scikit-learn>=1.4.0",
    "sentence-transformers>=2.2.0",  # Required for semantic search
]

[project.optional-dependencies]
full = [
    "transformers>=4.36.0",  # Optional: for high-accuracy sentiment
    "torch>=2.1.0",  # Optional: PyTorch for transformers
]

dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    # ... other dev dependencies ...
]
```

**Installation Instructions**:

```bash
# Lite installation (minimal memory, no transformers)
uv pip install redditsearch

# Full installation (includes transformer models)
uv pip install "redditsearch[full]"

# Development installation
uv pip install "redditsearch[full,dev]"
```

### 6. Post Filtering by URL Type (Self Posts vs Link Posts)

**Purpose**: Prioritize self-posts (text-only submissions) over link posts, as self-posts contain more genuine user discussions and pain points valuable for customer development.

**Problem**:
- Many subreddits like r/SaaS are filled with **link posts** (URLs to blogs, articles, promotional content)
- Link posts are often promotional or informational rather than conversational
- **Self-posts** (text-only submissions) are where users actually vent frustrations, ask for help, and discuss problems
- For customer development, self-posts have much higher signal-to-noise ratio

**Reddit Post Types**:
1. **Self Post** (`is_self=True`): Text-only submission with title and body (e.g., "I'm struggling with X, anyone have solutions?")
2. **Link Post** (`is_self=False`): URL to external content (e.g., link to blog post, article, image)
3. **Image/Video Post**: Technically link posts but to Reddit's image/video hosting

**Solution**: Add `--post-type` filter to CLI that allows filtering by post type.

**Database Schema Update** (`src/storage/models.py`):

Update the `posts` table to track post type:

```python
# Add to posts table schema
class Post(Base):
    __tablename__ = 'posts'

    # ... existing fields ...
    post_type: str  # 'self', 'link', 'image', 'video'
    is_self: bool  # True for self-posts, False for link/image/video
    url_domain: Optional[str]  # For link posts: domain name (e.g., 'medium.com')

    # Indexes
    # ... existing indexes ...
    # Add: (source, source_location, post_type, created_utc) for efficient filtering
```

**Reddit Plugin Update** (`src/sources/reddit/client.py`):

Extract post type information from PRAW:

```python
class RedditPlugin(DataSourcePlugin):
    def search(
        self,
        keywords: List[str],
        targets: List[str],
        time_filter: str,
        min_score: int,
        max_results: int,
        search_mode: str = 'hybrid',
        post_type: str = 'all'  # NEW: 'all', 'self', 'link', 'image', 'video'
    ) -> List[SourcePost]:
        """Search Reddit with post type filtering"""

        posts = []
        for subreddit_name in targets:
            subreddit = self.reddit.subreddit(subreddit_name)

            for submission in subreddit.new(limit=None):
                # Apply time filter, score filter...
                # ... existing filters ...

                # NEW: Apply post type filter
                if not self._matches_post_type(submission, post_type):
                    continue

                # Determine post type
                post_type_value = self._get_post_type(submission)
                url_domain = self._get_url_domain(submission) if not submission.is_self else None

                posts.append(SourcePost(
                    source='reddit',
                    source_id=submission.id,
                    title=submission.title,
                    body=submission.selftext if submission.is_self else '',
                    # ... other fields ...
                    post_type=post_type_value,  # NEW
                    is_self=submission.is_self,  # NEW
                    url_domain=url_domain,  # NEW
                    raw_data={'submission': submission}
                ))

        return posts

    def _matches_post_type(self, submission, filter_type: str) -> bool:
        """Check if submission matches post type filter"""
        if filter_type == 'all':
            return True
        elif filter_type == 'self':
            return submission.is_self
        elif filter_type == 'link':
            return not submission.is_self and not self._is_media_post(submission)
        elif filter_type == 'image':
            return self._is_image_post(submission)
        elif filter_type == 'video':
            return self._is_video_post(submission)
        else:
            return True

    def _get_post_type(self, submission) -> str:
        """Determine post type from submission"""
        if submission.is_self:
            return 'self'
        elif self._is_image_post(submission):
            return 'image'
        elif self._is_video_post(submission):
            return 'video'
        else:
            return 'link'

    def _is_media_post(self, submission) -> bool:
        """Check if post is image or video"""
        return self._is_image_post(submission) or self._is_video_post(submission)

    def _is_image_post(self, submission) -> bool:
        """Check if post is an image"""
        # Check for Reddit-hosted images
        if hasattr(submission, 'post_hint') and submission.post_hint == 'image':
            return True
        # Check URL extension
        if submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return True
        return False

    def _is_video_post(self, submission) -> bool:
        """Check if post is a video"""
        # Check for Reddit-hosted videos
        if hasattr(submission, 'is_video') and submission.is_video:
            return True
        # Check for video hosting domains
        video_domains = ['youtube.com', 'youtu.be', 'vimeo.com', 'streamable.com']
        if hasattr(submission, 'domain') and any(d in submission.domain for d in video_domains):
            return True
        return False

    def _get_url_domain(self, submission) -> Optional[str]:
        """Extract domain from submission URL"""
        if hasattr(submission, 'domain'):
            return submission.domain
        # Fallback: parse URL
        from urllib.parse import urlparse
        try:
            return urlparse(submission.url).netloc
        except:
            return None
```

**CLI Integration** (`src/cli/commands.py`):

Add `--post-type` option:

```python
@click.command()
@click.option('--preset', type=str, help='Use a pre-configured search preset')
@click.option('--keywords', type=str, help='Keywords to search for (comma-separated)')
@click.option('--subreddits', type=str, help='Subreddits to search (comma-separated)')
@click.option('--post-type',
              type=click.Choice(['all', 'self', 'link', 'image', 'video'], case_sensitive=False),
              default='all',
              help='Filter by post type (default: all)')
@click.option('--lite', is_flag=True, help='Use lite mode (low memory)')
# ... other options ...
def search(preset, keywords, subreddits, post_type, lite, **kwargs):
    """Search Reddit for customer development insights"""

    params = {
        # ... other params ...
        'post_type': post_type
    }

    # Show post type filter if not 'all'
    if post_type != 'all':
        console.print(f"[cyan]Filtering: {post_type} posts only[/cyan]")

    execute_search(params)
```

**Preset Configuration** (`config/sources/reddit.yaml`):

Update presets to prioritize self-posts by default:

```yaml
presets:
  # Customer development presets should focus on self-posts
  saas_pain_points:
    keywords: ["struggling with", "frustrated", "wish there was", "pay for"]
    subreddits: ["SaaS", "Entrepreneur", "startups"]
    days: 30
    min_score: 5
    post_type: "self"  # NEW: Prioritize self-posts for pain point discovery
    description: "Find SaaS opportunities with payment signals (self-posts only)"

  b2b_opportunities:
    keywords: ["enterprise need", "business tool", "company uses", "team needs"]
    subreddits: ["B2B_Sales", "sales", "marketing"]
    days: 30
    min_score: 3
    post_type: "self"  # NEW: Self-posts for genuine business discussions
    description: "B2B pain points and tool gaps (self-posts only)"

  developer_tools:
    keywords: ["dev tool", "build tool", "developer experience", "DX", "tooling"]
    subreddits: ["webdev", "programming", "devops"]
    days: 14
    min_score: 10
    post_type: "all"  # Allow link posts for dev tools (often share useful tools)
    description: "Developer tooling pain points and opportunities"

  competitive_intel:
    keywords: ["alternative to", "better than", "switching from", "migrating from"]
    subreddits: ["SaaS", "Entrepreneur", "startups"]
    days: 60
    min_score: 5
    post_type: "all"  # Allow all types for competitive intelligence
    description: "Competitor analysis and switching patterns"
```

**Dry-Run Enhancement** (`src/cli/validators.py`):

Show post type distribution in dry-run:

```python
def estimate_search_scope(params):
    """Enhanced dry-run with post type estimation"""

    # ... existing estimation code ...

    # NEW: Estimate post type distribution (based on subreddit characteristics)
    if params.get('post_type') != 'all':
        console.print(f"\n[cyan]Post Type Filter:[/cyan] {params['post_type']}")

        # Rough estimates based on subreddit type
        subreddit_stats = {
            'SaaS': {'self': 0.60, 'link': 0.30, 'image': 0.05, 'video': 0.05},
            'Entrepreneur': {'self': 0.70, 'link': 0.20, 'image': 0.05, 'video': 0.05},
            'startups': {'self': 0.65, 'link': 0.25, 'image': 0.05, 'video': 0.05},
            'webdev': {'self': 0.40, 'link': 0.40, 'image': 0.15, 'video': 0.05},
            'programming': {'self': 0.50, 'link': 0.30, 'image': 0.15, 'video': 0.05},
        }

        # Calculate estimated filtering impact
        avg_self_percentage = 0.60  # Default assumption
        for subreddit in params['subreddits']:
            if subreddit in subreddit_stats:
                avg_self_percentage = subreddit_stats[subreddit]['self']
                break

        filter_type = params['post_type']
        if filter_type == 'self':
            reduction = avg_self_percentage
        elif filter_type == 'link':
            reduction = 1 - avg_self_percentage
        else:
            reduction = 1.0

        estimated_posts_before = params['max_posts']
        estimated_posts_after = int(estimated_posts_before * reduction)

        console.print(f"  [dim]Expected {filter_type} posts: ~{estimated_posts_after}/{estimated_posts_before} ({reduction*100:.0f}%)[/dim]")
        console.print(f"  [dim]Reason: Self-posts contain more genuine discussions[/dim]")
```

**CLI Usage Examples**:

```bash
# Search only self-posts (text discussions) - RECOMMENDED for customer development
redditsearch search \
  --keywords "pay for,struggling with" \
  --subreddits "SaaS,Entrepreneur" \
  --post-type self \
  --days 30

# Search only link posts (to find what articles/tools people share)
redditsearch search \
  --keywords "tool,solution" \
  --subreddits "productivity,SaaS" \
  --post-type link \
  --days 30

# Search all post types (default behavior)
redditsearch search \
  --keywords "pay for" \
  --subreddits "SaaS" \
  --post-type all \
  --days 30

# Use preset (automatically applies post_type from preset config)
redditsearch search --preset saas_pain_points
# This preset uses post_type=self by default

# Dry run shows post type filter impact
redditsearch search \
  --keywords "pay for" \
  --subreddits "SaaS" \
  --post-type self \
  --dry-run

# Output:
# Search Preview (Dry Run)
# ...
# Post Type Filter: self
#   Expected self posts: ~60/100 (60%)
#   Reason: Self-posts contain more genuine discussions
```

**Why Self-Posts for Customer Development**:

Include this explanation in README.md:

```markdown
### Post Type Filtering

For customer development, **self-posts (text-only)** are more valuable than link posts:

**Self-Posts** (`--post-type self`):
- ✅ Users write original thoughts and frustrations
- ✅ Genuine discussions and problem descriptions
- ✅ Higher engagement in comments
- ✅ Payment signals ("I would pay for...")
- Example: "I'm struggling to find a good tool for X. Currently using Y but it's frustrating because..."

**Link Posts** (`--post-type link`):
- ⚠️ Often promotional or informational
- ⚠️ Less conversational context
- ⚠️ Fewer genuine pain points
- Example: [Link to blog post about "10 Best Tools for X"]

**Recommendation**: Use `--post-type self` for customer development searches, or use presets like `saas_pain_points` that default to self-posts.
```

**Visualization Enhancement** (`src/visualization/charts.py`):

Add post type breakdown to dashboard:

```python
def create_post_type_chart(df):
    """Create pie chart showing post type distribution"""

    post_type_counts = df['post_type'].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=post_type_counts.index,
        values=post_type_counts.values,
        marker=dict(colors=['#2ecc71', '#3498db', '#e74c3c', '#f39c12']),
        hovertemplate='%{label}: %{value} posts (%{percent})<extra></extra>'
    )])

    fig.update_layout(
        title='Post Type Distribution',
        showlegend=True
    )

    return fig
```

**Report Template Update** (`src/visualization/templates/report.html`):

Add post type statistics to summary section:

```html
<div class="summary-stats">
    <h2>Search Summary</h2>
    <ul>
        <li><strong>Total Posts:</strong> {{ total_posts }}</li>
        <li><strong>Self Posts:</strong> {{ self_posts }} ({{ self_percentage }}%)</li>
        <li><strong>Link Posts:</strong> {{ link_posts }} ({{ link_percentage }}%)</li>
        <li><strong>Keyword Matches:</strong> {{ total_matches }}</li>
        <li><strong>Payment Signals:</strong> {{ payment_signals }}</li>
    </ul>
</div>

<!-- Add post type distribution chart -->
<div class="chart-container">
    {{ post_type_chart | safe }}
</div>
```

**Settings Configuration** (`config/settings.py`):

```python
class Settings(BaseSettings):
    # ... other settings ...

    # Post type filtering
    DEFAULT_POST_TYPE: str = 'all'  # Options: 'all', 'self', 'link', 'image', 'video'

    # For customer development, recommend self-posts
    CUSTOMER_DEV_POST_TYPE: str = 'self'
```

**Database Query Optimization**:

Add index for efficient post type filtering:

```python
# In database migration
op.create_index(
    'ix_posts_source_location_type_created',
    'posts',
    ['source', 'source_location', 'post_type', 'created_utc']
)
```

**Testing** (`tests/test_sources/test_reddit.py`):

```python
def test_post_type_filtering():
    """Test post type detection and filtering"""

    plugin = RedditPlugin()

    # Mock self-post
    self_post = Mock(is_self=True, url='https://reddit.com/...')
    assert plugin._get_post_type(self_post) == 'self'
    assert plugin._matches_post_type(self_post, 'self') == True
    assert plugin._matches_post_type(self_post, 'link') == False

    # Mock link post
    link_post = Mock(is_self=False, url='https://medium.com/article', domain='medium.com')
    assert plugin._get_post_type(link_post) == 'link'
    assert plugin._matches_post_type(link_post, 'link') == True
    assert plugin._matches_post_type(link_post, 'self') == False

    # Mock image post
    image_post = Mock(is_self=False, post_hint='image', url='https://i.redd.it/abc.jpg')
    assert plugin._get_post_type(image_post) == 'image'
    assert plugin._matches_post_type(image_post, 'image') == True
    assert plugin._matches_post_type(image_post, 'self') == False

    # Test 'all' filter
    assert plugin._matches_post_type(self_post, 'all') == True
    assert plugin._matches_post_type(link_post, 'all') == True
```

**Phase 3 Update**:

Add to Phase 3 (Data Sources & Core Search) testing requirements:
- Test post type detection for self-posts, link posts, image posts, video posts
- Test `--post-type` CLI filter with all options
- Verify preset defaults apply post type correctly
- Test dry-run shows post type filter impact
- Verify database indexes for post type filtering
- Test post type visualization in dashboard

**Impact Summary**:

| Aspect | Before | After |
|--------|--------|-------|
| **Default Behavior** | All post types included | All post types (backward compatible) |
| **Customer Dev Presets** | Mixed post types | Self-posts only (higher signal) |
| **CLI Flexibility** | No filtering | `--post-type self/link/image/video/all` |
| **Database** | No post type tracking | post_type, is_self, url_domain fields |
| **Visualization** | Not shown | Post type distribution chart |
| **Documentation** | Not mentioned | Clear guidance on self vs link posts |

**Key Benefits**:
1. **Higher Signal-to-Noise**: Self-posts contain genuine discussions vs promotional links
2. **Faster Processing**: Filtering reduces posts to process
3. **Better Insights**: Focus on where users actually discuss pain points
4. **Flexibility**: Still supports all post types when needed (competitive intel, tool discovery)
5. **Backward Compatible**: Default is 'all', existing behavior unchanged

### 7. Hype Filter (Anti-Spam / Self-Promotion Detection)

**Purpose**: Distinguish genuine pain points from spam, affiliate marketing, and self-promotion to keep customer development analysis focused on authentic user needs.

**Problem**:
- Many subreddits contain **self-promotional posts** disguised as pain points ("I built this tool..." followed by affiliate link)
- **Affiliate marketers** create fake discussions to promote products
- **"Hype" language** often signals promotional content rather than genuine frustration
- These posts pollute customer development research by masquerading as user needs

**Examples of Spam vs Genuine**:

**Spam/Promotional**:
- "Check out my new SaaS tool! [affiliate link]"
- "I've been using [Product X] and it's amazing! Get 20% off with code..."
- "DM me for the solution, I've helped 100+ businesses..."

**Genuine Pain Point**:
- "I'm struggling to find a tool that does X without costing $200/month"
- "Currently using [Tool] but frustrated with missing Y feature"
- "Does anyone know a solution for Z? Been searching for weeks"

**Solution**: Add configurable spam detection filter with multiple strategies.

**Implementation** (`src/analysis/spam_filter.py`):

```python
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class SpamSignalType(Enum):
    """Types of spam/promotional signals"""
    AFFILIATE = "affiliate_marketing"
    SELF_PROMO = "self_promotion"
    DM_SOLICITATION = "dm_solicitation"
    DISCOUNT_CODE = "discount_code"
    HYPE_LANGUAGE = "hype_language"
    EXTERNAL_LINK = "external_link_spam"
    FAKE_QUESTION = "fake_question"

@dataclass
class SpamSignal:
    """Detected spam/promotional signal"""
    signal_type: SpamSignalType
    matched_pattern: str
    matched_text: str
    confidence: float  # 0.0-1.0
    context: str

class HypeFilter:
    """
    Detect and filter spam, self-promotion, and affiliate marketing

    Uses regex patterns and heuristics to flag promotional content
    while preserving genuine pain points.
    """

    def __init__(self):
        # Affiliate marketing patterns
        self.affiliate_patterns = [
            r'affiliate\s+link',
            r'referral\s+(?:link|code)',
            r'use\s+(?:my\s+)?code\s+[A-Z0-9]+',
            r'get\s+\d+%\s+off',
            r'discount\s+code',
            r'promo\s+code',
            r'bit\.ly/',  # URL shorteners often used for affiliate tracking
            r'geni\.us/',  # Amazon affiliate shortener
        ]

        # Self-promotion patterns
        self.self_promo_patterns = [
            r'(?:i|we)\s+(?:built|created|made|developed)\s+(?:a|an|this)\s+(?:tool|app|saas|platform|solution)',
            r'check\s+out\s+(?:my|our)\s+(?:tool|app|product|startup|company)',
            r'(?:my|our)\s+(?:startup|company|product|tool)\s+(?:solves|fixes|handles)',
            r'launched\s+(?:my|our)\s+(?:product|tool|startup)',
            r'shameless\s+plug',
            r'(?:my|our)\s+(?:company|startup|product)\s+does\s+(?:this|exactly\s+this)',
        ]

        # DM solicitation (often spam)
        self.dm_solicitation_patterns = [
            r'dm\s+me',
            r'send\s+me\s+a\s+(?:dm|message)',
            r'pm\s+me\s+for',
            r'message\s+me\s+for\s+(?:more|details|info)',
            r'reach\s+out\s+to\s+me',
            r'contact\s+me\s+(?:at|for)',
        ]

        # Discount/pricing manipulation
        self.discount_patterns = [
            r'\d+%\s+off',
            r'limited\s+time\s+offer',
            r'special\s+(?:offer|discount|deal)',
            r'exclusive\s+(?:offer|discount|deal)',
            r'early\s+bird\s+(?:pricing|discount)',
            r'flash\s+sale',
        ]

        # Excessive hype language (often fake enthusiasm)
        self.hype_patterns = [
            r'(?:life-?changing|game-?changing|revolutionary)',
            r'this\s+will\s+(?:blow\s+your\s+mind|change\s+everything)',
            r'you\s+won\'?t\s+believe',
            r'secret\s+(?:method|technique|strategy)',
            r'(?:insane|crazy|unbelievable)\s+(?:results|growth)',
            r'absolute\s+best\s+(?:tool|solution|way)',
            r'ultimate\s+(?:guide|solution|tool)',
        ]

        # External links with common spam domains
        self.spam_domains = [
            'bit.ly',
            'tinyurl.com',
            'geni.us',
            'amzn.to',
            'clickbank',
            'warriorplus',
        ]

        # Fake question patterns (promotional questions)
        self.fake_question_patterns = [
            r'what\s+do\s+you\s+think\s+(?:of|about)\s+\[.*?\]\??\s*(?:http|www)',  # "What do you think of [My Tool]? link..."
            r'has\s+anyone\s+tried\s+\[.*?\]\??\s*(?:http|www)',  # Often followed by affiliate link
        ]

    def analyze(self, text: str, url: Optional[str] = None) -> Dict:
        """
        Analyze text for spam/promotional signals

        Args:
            text: Post or comment text to analyze
            url: Optional URL if it's a link post

        Returns:
            Dictionary with spam analysis results
        """
        signals = []

        text_lower = text.lower()

        # Check affiliate marketing patterns
        for pattern in self.affiliate_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                signals.append(SpamSignal(
                    signal_type=SpamSignalType.AFFILIATE,
                    matched_pattern=pattern,
                    matched_text=match.group(),
                    confidence=0.9,
                    context=self._extract_context(text, match.start(), match.end())
                ))

        # Check self-promotion patterns
        for pattern in self.self_promo_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                signals.append(SpamSignal(
                    signal_type=SpamSignalType.SELF_PROMO,
                    matched_pattern=pattern,
                    matched_text=match.group(),
                    confidence=0.85,
                    context=self._extract_context(text, match.start(), match.end())
                ))

        # Check DM solicitation
        for pattern in self.dm_solicitation_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                signals.append(SpamSignal(
                    signal_type=SpamSignalType.DM_SOLICITATION,
                    matched_pattern=pattern,
                    matched_text=match.group(),
                    confidence=0.8,
                    context=self._extract_context(text, match.start(), match.end())
                ))

        # Check discount codes
        for pattern in self.discount_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                signals.append(SpamSignal(
                    signal_type=SpamSignalType.DISCOUNT_CODE,
                    matched_pattern=pattern,
                    matched_text=match.group(),
                    confidence=0.95,
                    context=self._extract_context(text, match.start(), match.end())
                ))

        # Check hype language
        for pattern in self.hype_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                signals.append(SpamSignal(
                    signal_type=SpamSignalType.HYPE_LANGUAGE,
                    matched_pattern=pattern,
                    matched_text=match.group(),
                    confidence=0.7,  # Lower confidence, can be genuine excitement
                    context=self._extract_context(text, match.start(), match.end())
                ))

        # Check fake questions
        for pattern in self.fake_question_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)  # Not lowercased, need to preserve []
            for match in matches:
                signals.append(SpamSignal(
                    signal_type=SpamSignalType.FAKE_QUESTION,
                    matched_pattern=pattern,
                    matched_text=match.group(),
                    confidence=0.85,
                    context=self._extract_context(text, match.start(), match.end())
                ))

        # Check URL for spam domains
        if url:
            for domain in self.spam_domains:
                if domain in url.lower():
                    signals.append(SpamSignal(
                        signal_type=SpamSignalType.EXTERNAL_LINK,
                        matched_pattern=domain,
                        matched_text=url,
                        confidence=0.8,
                        context=f"Link post to: {url}"
                    ))

        # Calculate overall spam score
        spam_score = self._calculate_spam_score(signals)

        return {
            'is_likely_spam': spam_score > 0.5,
            'spam_score': spam_score,  # 0.0 (genuine) to 1.0 (definitely spam)
            'spam_signals': [
                {
                    'type': s.signal_type.value,
                    'matched_text': s.matched_text,
                    'confidence': s.confidence,
                    'context': s.context[:100] + '...' if len(s.context) > 100 else s.context
                }
                for s in signals
            ],
            'signal_count': len(signals),
            'signal_types': list(set(s.signal_type.value for s in signals))
        }

    def _extract_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Extract context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        return text[context_start:context_end]

    def _calculate_spam_score(self, signals: List[SpamSignal]) -> float:
        """
        Calculate overall spam probability

        Uses weighted combination of signal confidences:
        - Multiple signals increase confidence
        - High-confidence signals (discount codes, affiliates) weighted heavily
        - Lower-confidence signals (hype language) weighted less
        """
        if not signals:
            return 0.0

        # Group by type
        signal_types = {}
        for signal in signals:
            if signal.signal_type not in signal_types:
                signal_types[signal.signal_type] = []
            signal_types[signal.signal_type].append(signal)

        # Weight different signal types
        weights = {
            SpamSignalType.AFFILIATE: 0.3,
            SpamSignalType.DISCOUNT_CODE: 0.3,
            SpamSignalType.SELF_PROMO: 0.2,
            SpamSignalType.DM_SOLICITATION: 0.15,
            SpamSignalType.FAKE_QUESTION: 0.15,
            SpamSignalType.EXTERNAL_LINK: 0.1,
            SpamSignalType.HYPE_LANGUAGE: 0.05,
        }

        score = 0.0
        for signal_type, type_signals in signal_types.items():
            # Take max confidence for this signal type
            max_confidence = max(s.confidence for s in type_signals)
            # Apply weight
            score += max_confidence * weights.get(signal_type, 0.1)

        # Cap at 1.0
        return min(score, 1.0)
```

**Database Integration** (`src/storage/models.py`):

Add spam detection results to posts/comments:

```python
class Post(Base):
    __tablename__ = 'posts'

    # ... existing fields ...
    spam_score: float = 0.0  # 0.0 (genuine) to 1.0 (spam)
    is_likely_spam: bool = False
    spam_signals: str = None  # JSON array of detected signals
```

**CLI Integration** (`src/cli/commands.py`):

Add `--filter-spam` option:

```python
@click.command()
@click.option('--preset', type=str, help='Use a pre-configured search preset')
@click.option('--keywords', type=str, help='Keywords to search for (comma-separated)')
@click.option('--subreddits', type=str, help='Subreddits to search (comma-separated)')
@click.option('--post-type', type=click.Choice(['all', 'self', 'link', 'image', 'video']))
@click.option('--filter-spam',
              is_flag=True,
              help='Filter out likely spam/self-promotional posts')
@click.option('--spam-threshold',
              type=float,
              default=0.5,
              help='Spam score threshold (0.0-1.0, default 0.5)')
# ... other options ...
def search(preset, keywords, subreddits, post_type, filter_spam, spam_threshold, **kwargs):
    """Search Reddit for customer development insights"""

    params = {
        # ... other params ...
        'filter_spam': filter_spam,
        'spam_threshold': spam_threshold
    }

    if filter_spam:
        console.print(f"[cyan]Spam filtering enabled (threshold: {spam_threshold})[/cyan]")
        console.print(f"[dim]Filtering self-promotional and affiliate marketing content[/dim]\n")

    execute_search(params)
```

**Search Engine Integration** (`src/core/search_engine.py`):

Apply spam filter during search:

```python
from src.analysis.spam_filter import HypeFilter

class SearchEngine:
    def __init__(self):
        self.spam_filter = HypeFilter()
        # ... other initialization ...

    def process_post(self, post: SourcePost, filter_spam: bool = False, spam_threshold: float = 0.5):
        """Process a post with optional spam filtering"""

        # Analyze for spam
        spam_analysis = self.spam_filter.analyze(
            text=f"{post.title}\n\n{post.body}",
            url=post.url if not post.is_self else None
        )

        # Store spam analysis
        post.spam_score = spam_analysis['spam_score']
        post.is_likely_spam = spam_analysis['is_likely_spam']
        post.spam_signals = json.dumps(spam_analysis['spam_signals'])

        # Filter if requested
        if filter_spam and spam_analysis['spam_score'] >= spam_threshold:
            logger.info(f"Filtered spam post: {post.title} (score: {spam_analysis['spam_score']:.2f})")
            return None  # Skip this post

        return post
```

**Preset Configuration** (`config/sources/reddit.yaml`):

Update presets to filter spam by default for customer development:

```yaml
presets:
  saas_pain_points:
    keywords: ["struggling with", "frustrated", "wish there was", "pay for"]
    subreddits: ["SaaS", "Entrepreneur", "startups"]
    days: 30
    min_score: 5
    post_type: "self"
    filter_spam: true  # NEW: Filter spam by default
    spam_threshold: 0.5
    description: "Find SaaS opportunities with payment signals (spam filtered)"

  b2b_opportunities:
    keywords: ["enterprise need", "business tool", "company uses", "team needs"]
    subreddits: ["B2B_Sales", "sales", "marketing"]
    days: 30
    min_score: 3
    post_type: "self"
    filter_spam: true  # NEW: Filter spam
    spam_threshold: 0.5
    description: "B2B pain points and tool gaps (spam filtered)"
```

**Visualization Enhancement** (`src/visualization/charts.py`):

Add spam detection statistics to dashboard:

```python
def create_spam_detection_chart(df):
    """Create spam detection summary chart"""

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Spam Score Distribution', 'Top Spam Signal Types'),
        specs=[[{'type': 'histogram'}, {'type': 'bar'}]]
    )

    # Spam score distribution
    fig.add_trace(go.Histogram(
        x=df['spam_score'],
        nbinsx=20,
        name='Spam Scores',
        marker_color='#e74c3c'
    ), row=1, col=1)

    # Add threshold line
    fig.add_vline(x=0.5, line_dash="dash", line_color="red",
                  annotation_text="Threshold", row=1, col=1)

    # Signal type counts
    spam_posts = df[df['is_likely_spam'] == True]
    if len(spam_posts) > 0:
        # Parse signal types from JSON
        signal_types = []
        for signals_json in spam_posts['spam_signals']:
            if signals_json:
                signals = json.loads(signals_json)
                for signal in signals:
                    signal_types.append(signal['type'])

        signal_counts = pd.Series(signal_types).value_counts()

        fig.add_trace(go.Bar(
            x=signal_counts.values,
            y=signal_counts.index,
            orientation='h',
            marker_color='#e74c3c'
        ), row=1, col=2)

    fig.update_layout(
        title='Spam Detection Analysis',
        showlegend=False,
        height=400
    )

    return fig
```

**CLI Usage Examples**:

```bash
# Search with spam filtering enabled (recommended for customer development)
redditsearch search \
  --keywords "pay for,struggling with" \
  --subreddits "SaaS,Entrepreneur" \
  --filter-spam \
  --days 30

# Use preset with spam filtering (enabled by default in presets)
redditsearch search --preset saas_pain_points
# Spam filtering already enabled in preset

# Adjust spam threshold (stricter)
redditsearch search \
  --preset saas_pain_points \
  --spam-threshold 0.3
# Lower threshold = more aggressive filtering

# Adjust spam threshold (looser)
redditsearch search \
  --preset saas_pain_points \
  --spam-threshold 0.7
# Higher threshold = only filter obvious spam

# Disable spam filtering (see everything)
redditsearch search \
  --keywords "tool" \
  --subreddits "SaaS" \
  --filter-spam false

# Dry run shows spam filtering status
redditsearch search \
  --preset saas_pain_points \
  --dry-run

# Output:
# Search Preview (Dry Run)
# ...
# Spam Filtering: Enabled (threshold: 0.5)
#   Expected spam filtered: ~15-20%
#   Signals detected: affiliate, self_promo, dm_solicitation
```

**Report Summary Enhancement**:

Add spam statistics to report summary:

```html
<div class="spam-detection-summary">
    <h3>Spam Detection Summary</h3>
    <ul>
        <li><strong>Posts Analyzed:</strong> {{ total_posts }}</li>
        <li><strong>Spam Detected:</strong> {{ spam_posts }} ({{ spam_percentage }}%)</li>
        <li><strong>Posts After Filtering:</strong> {{ genuine_posts }}</li>
        <li><strong>Top Spam Signals:</strong> {{ top_spam_signals }}</li>
    </ul>

    <div class="spam-examples">
        <h4>Example Spam Filtered:</h4>
        <ul>
        {% for example in spam_examples[:3] %}
            <li>
                <strong>{{ example.title }}</strong><br>
                <span class="spam-score">Spam Score: {{ example.spam_score }}</span><br>
                <span class="spam-signals">Signals: {{ example.signal_types }}</span>
            </li>
        {% endfor %}
        </ul>
    </div>
</div>
```

**Settings Configuration** (`config/settings.py`):

```python
class Settings(BaseSettings):
    # ... other settings ...

    # Spam filtering
    SPAM_FILTER_ENABLED: bool = True  # Default: enabled
    SPAM_THRESHOLD: float = 0.5  # 0.0 (strict) to 1.0 (loose)

    # For customer development, recommend spam filtering
    CUSTOMER_DEV_FILTER_SPAM: bool = True
```

**Spam Threshold Guidance**:

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| **0.3** | Very Strict | Only want obvious genuine pain points, remove any hint of promotion |
| **0.5** | Balanced (Default) | Good for customer development, filters clear spam while keeping borderline |
| **0.7** | Lenient | Keep most content, only filter obvious spam/affiliate links |
| **1.0** | Disabled | No filtering, see everything (useful for analysis/tuning) |

**Testing** (`tests/test_analysis/test_spam_filter.py`):

```python
def test_spam_filter():
    """Test spam detection patterns"""

    filter = HypeFilter()

    # Test affiliate marketing detection
    affiliate_text = "Check out this tool! Use code SAVE20 for 20% off: bit.ly/affiliate"
    result = filter.analyze(affiliate_text)
    assert result['is_likely_spam'] == True
    assert result['spam_score'] > 0.5
    assert any(s['type'] == 'discount_code' for s in result['spam_signals'])

    # Test self-promotion detection
    promo_text = "I built a SaaS tool that solves this exact problem! Check it out."
    result = filter.analyze(promo_text)
    assert result['is_likely_spam'] == True
    assert any(s['type'] == 'self_promotion' for s in result['spam_signals'])

    # Test genuine pain point (should NOT be flagged)
    genuine_text = "I'm struggling to find a good tool for X. Currently paying $100/mo for Y but it's missing Z feature. Would happily pay for something better."
    result = filter.analyze(genuine_text)
    assert result['is_likely_spam'] == False
    assert result['spam_score'] < 0.5

    # Test DM solicitation
    dm_text = "I can help with this. DM me for more details on my solution."
    result = filter.analyze(dm_text)
    assert result['is_likely_spam'] == True
    assert any(s['type'] == 'dm_solicitation' for s in result['spam_signals'])
```

**Phase 5 Update**:

Add to Phase 5 (Analysis Pipeline) requirements:
- Implement HypeFilter spam detection
- Test spam pattern matching with known examples
- Test spam score calculation
- Test filtering integration in search engine
- Verify spam statistics in dashboard

**Why This Matters for Customer Development**:

Include in README.md:

```markdown
### Spam Filtering (Hype Filter)

For accurate customer development, it's critical to distinguish **genuine pain points** from **promotional noise**.

**What Gets Filtered**:
- ❌ Affiliate marketing links and discount codes
- ❌ Self-promotional posts ("I built a tool...")
- ❌ DM solicitations ("Contact me for...")
- ❌ Excessive hype language ("Life-changing solution!")
- ❌ Fake questions with affiliate links

**What Gets Kept**:
- ✅ Genuine user frustrations
- ✅ Real payment willingness signals
- ✅ Authentic problem descriptions
- ✅ User discussions about existing tools

**Usage**:
```bash
# Enable spam filtering (recommended)
redditsearch search --preset saas_pain_points --filter-spam

# Adjust threshold for stricter filtering
redditsearch search --preset saas_pain_points --spam-threshold 0.3
```

**Default Behavior**: Spam filtering is **enabled by default** in customer development presets to ensure clean, actionable insights.
```

**Impact Summary**:

| Aspect | Before | After |
|--------|--------|-------|
| **Spam Detection** | None | Multi-pattern detection with confidence scoring |
| **Data Quality** | Mixed (spam + genuine) | High quality (spam filtered) |
| **Default Presets** | No filtering | Spam filtering enabled |
| **Flexibility** | N/A | Adjustable threshold (0.0-1.0) |
| **Transparency** | N/A | Spam stats shown in reports |

**Key Benefits**:
1. **Cleaner Insights**: Focus on genuine pain points, not marketing
2. **Better Validation**: Payment signals from real users, not promoters
3. **Time Savings**: No manual filtering of spam needed
4. **Transparency**: See what was filtered and why
5. **Configurable**: Adjust threshold based on your needs

### 6. Reddit API Setup
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

### 3. Cross-Search Deduplication Behavior

**Question**: If I search the same subreddit twice with different keywords, will the system re-process the same posts?

**Answer**: The system intelligently avoids re-fetching data from Reddit's API while still analyzing posts for new keywords. Here's exactly what happens:

#### Scenario: Two Searches on Same Subreddit

**Search 1**: Keywords = "pay for", Subreddit = "SaaS"
**Search 2**: Keywords = "frustrated with", Subreddit = "SaaS"

#### What Happens Internally:

**For Posts/Submissions**:

1. **Search 1 execution**:
   - Fetches 100 posts from r/SaaS via Reddit API
   - Saves each post to `submissions` table with unique `reddit_id`
   - Records `first_seen_search_id = search_1`
   - `seen_count = 1`

2. **Search 2 execution** (same subreddit, overlapping posts):
   - Fetches "same" 100 posts from r/SaaS via Reddit API (Reddit API call required for time-filtered queries)
   - For each post, checks `submissions` table by `reddit_id`
   - **If post exists**:
     - **Does NOT re-fetch post data** (title, body, author already in DB)
     - Increments `seen_count` to 2
     - Returns existing database record
   - **If post is new** (posted after Search 1):
     - Creates new record with `first_seen_search_id = search_2`

**For Comments**:

- Comments **are stored once** per unique `reddit_id` in `comments` table
- Same deduplication logic as posts (seen_count incremented)
- **Not re-fetched** from Reddit API if already in database

**For Keyword Matches**:

- **This is where re-analysis happens!**
- Even if a post/comment exists in database, it's **re-scanned for NEW keywords**
- Each keyword match creates a **new row** in `keyword_matches` table:
  - Links to existing `submission_id` or `comment_id`
  - Links to new `search_id` (search_2)
  - Stores keyword-specific context extraction

**Example**:

Post ABC123 contains: "I'm frustrated with current tools and would pay for a better solution"

- **Search 1** (keyword: "pay for"):
  - Fetches post from Reddit → saves to `submissions`
  - Finds "pay for" → saves to `keyword_matches` (search_id=1, keyword="pay for")

- **Search 2** (keyword: "frustrated with"):
  - Reddit API returns same post in query results (time-filtered)
  - **Skips re-saving post data** (already in `submissions`)
  - Increments `seen_count` from 1 → 2
  - Scans existing post body for "frustrated with"
  - **Creates new keyword match**: `keyword_matches` (search_id=2, keyword="frustrated with")

#### Efficiency Benefits:

**What IS re-fetched** (unavoidable):
- Initial Reddit API query to get post IDs for time window (Reddit API limitation)
- This counts against rate limit but is required to know which posts exist

**What is NOT re-fetched** (efficient):
- Post metadata (title, body, author, scores) - read from database
- Comment trees - read from database
- Comment bodies - read from database

**Net Result**:
- **API requests**: Still need to query subreddit (required by Reddit API design)
- **Data transfer**: Minimal (only post IDs, not full content)
- **Processing time**: Much faster (no comment tree traversal, read from DB)
- **Database**: Posts/comments stored once, keyword matches linked via foreign keys

#### Implementation Details:

**Search Engine Logic** (`src/scraper/search_engine.py`):

```python
def execute_search(self, search_id, keywords, subreddits, time_filter):
    """
    Execute search across subreddits

    Handles deduplication transparently:
    - Reddit API calls fetch post IDs (unavoidable)
    - get_or_create_submission() handles dedup
    - Comments fetched from DB if available
    - Keyword analysis runs on all posts (new and existing)
    """

    for subreddit_name in subreddits:
        subreddit = self.reddit.subreddit(subreddit_name)

        # Reddit API call (required to get posts in time window)
        for praw_submission in subreddit.search(...):

            # Check if post already in database
            db_submission, is_new = self.repo.get_or_create_submission(
                praw_submission,
                search_id
            )

            if is_new:
                # Fetch and store comments from Reddit API
                self.fetch_and_store_comments(praw_submission, search_id)
            else:
                # Load comments from database (much faster)
                db_comments = self.repo.get_comments_for_submission(
                    db_submission.id
                )

            # ALWAYS analyze for keywords (both new and existing posts)
            self.analyze_keywords(
                db_submission,
                db_comments,
                keywords,
                search_id
            )
```

**Keyword Match Storage**:

```python
# keyword_matches table schema
class KeywordMatch:
    id: int  # Primary key
    search_id: int  # Foreign key - links to specific search
    submission_id: int  # Foreign key - links to post
    comment_id: int  # Foreign key - links to comment (if match in comment)
    keyword: str  # The keyword that matched
    context_before: str
    matched_text: str
    context_after: str
    full_paragraph: str

# This allows:
# - Same post to have matches for different keywords across searches
# - Query: "Show me all 'pay for' matches from search_1"
# - Query: "Show me all 'frustrated with' matches from search_2"
# - Query: "Show me all matches across all searches for post ABC123"
```

#### Performance Comparison:

**Scenario**: Search r/SaaS with "pay for" (100 posts, 1500 comments)

**First search**:
- API requests: ~100 (fetch posts + comments)
- Time: ~5 minutes (with rate limiting)
- Database: 100 posts, 1500 comments, 50 keyword matches

**Second search** (same subreddit, different keyword "frustrated with"):
- API requests: ~10 (query subreddit for post IDs, most posts already cached)
- Time: ~30 seconds (mostly database queries + keyword scanning)
- Database: Same 100 posts (seen_count++), same 1500 comments, +30 NEW keyword matches

**Time savings**: 90% faster for subsequent searches on same subreddit

#### User-Facing Behavior:

**CLI Output for Search 2**:

```
Searching r/SaaS for "frustrated with"...

Posts found: 100
  ├─ New posts: 5 (fetched from Reddit)
  └─ Cached posts: 95 (loaded from database)

Comments analyzed: 1500
  ├─ New comments: 75 (fetched from Reddit)
  └─ Cached comments: 1425 (loaded from database)

Keyword matches: 30 new matches found

Time: 45 seconds (vs 5m for fresh search)
API requests: 15 (vs 120 for fresh search)

✓ Search complete! Run `redditsearch report <search_id>` to visualize.
```

#### Key Takeaways:

✅ **Posts/comments are stored once** (by unique `reddit_id`)
✅ **Keyword analysis happens every search** (new matches created)
✅ **API calls reduced** for overlapping content (read from DB)
✅ **Faster subsequent searches** on same subreddits
✅ **Separate reports per search** (different keyword focus)
✅ **Efficient storage** (no duplicate content, only duplicate match links)

### 5. Comment Tree Traversal and Depth Configuration

**Configurable Comment Depth**:

Comment depth significantly affects data quality, API usage, and search time. Make this configurable to let users choose their tradeoff.

**Understanding Comment Depth**:

| Depth Setting | API Requests | Time Impact | Use Case | What You Get |
|---------------|--------------|-------------|----------|--------------|
| **0** | Minimal | Fastest | Quick overview | Only top-level comments (direct replies to post) |
| **1-2** | Low | Fast | Surface-level insights | Top comments + first replies (most upvoted content) |
| **3-10** | Moderate | Medium | Balanced | Most discussions, includes follow-ups |
| **32+ (Default)** | High | Slow | Deep dive | Full conversations, niche discussions in deep threads |
| **None** | Very High | Slowest | Comprehensive | Every single comment (may hit rate limits) |

**Recommendation**: Start with **32** (default) for balanced coverage, then adjust:
- **Speed priority**: Use 3-5 for faster searches
- **Quality priority**: Use 32+ to capture deep discussions
- **Comprehensive**: Use None only for small subreddits or specific high-value threads

**CLI Configuration**:
```bash
# Fast search (top-level comments only)
redditsearch search --keywords "pay for" --subreddits "SaaS" --comment-depth 0

# Balanced (default - gets most valuable content)
redditsearch search --keywords "pay for" --subreddits "SaaS" --comment-depth 32

# Comprehensive (slow, use for specific high-value searches)
redditsearch search --keywords "pay for" --subreddits "SaaS" --comment-depth none
```

**Settings Configuration** (`config/settings.py`):
```python
class Settings(BaseSettings):
    # ... other settings ...

    # Comment depth configuration
    COMMENT_DEPTH_LIMIT: Optional[int] = 32  # Default: balanced
    # None = fetch all comments (slow)
    # 0 = top-level only (fast)
    # 32 = balanced (recommended)
```

**Implementation** (`src/sources/reddit/parser.py`):
```python
def extract_comments(
    submission,
    keyword_patterns,
    depth_limit: Optional[int] = 32
):
    """
    Extract comments from Reddit submission with configurable depth

    Args:
        submission: PRAW submission object
        keyword_patterns: List of keyword patterns to match
        depth_limit: Max depth for replace_more()
            - None: Fetch all comments (slow, may hit rate limits)
            - 0: Top-level comments only (fastest)
            - 32: Balanced (default, recommended)
            - Higher: More comprehensive but slower

    Returns:
        List of extracted comments with keyword matches
    """

    # Replace MoreComments objects with limit
    # This determines how many "load more comments" we expand
    if depth_limit is None:
        # Fetch everything (warning: slow and may hit rate limits)
        submission.comments.replace_more(limit=None)
    else:
        # Fetch up to depth_limit "more comments" expansions
        submission.comments.replace_more(limit=depth_limit)

    comments = []

    # Flatten comment tree
    for comment in submission.comments.list():
        if hasattr(comment, 'body'):  # Skip deleted/removed comments
            # Check for keyword matches
            # Extract context (full paragraph)
            # Save to database with depth information
            comments.append(comment)

    return comments
```

**Dry Run Enhancement**:
Update dry run to show depth impact:
```python
# In dry_run estimation
if comment_depth == 0:
    estimated_comments = estimated_posts * 5  # Top-level only
elif comment_depth <= 5:
    estimated_comments = estimated_posts * 10  # Shallow threads
elif comment_depth <= 32:
    estimated_comments = estimated_posts * 15  # Balanced (default)
else:
    estimated_comments = estimated_posts * 25  # Deep threads

console.print(f"  • Comment depth: {comment_depth if comment_depth else 'top-level only'}")
console.print(f"  • Comments to scan: ~{estimated_comments:,}")
```

**When to Use Different Depths**:

1. **Depth 0 (Top-level only)**:
   - Quick validation of a keyword's presence
   - Testing search parameters
   - High-volume subreddits with many posts
   - Example: "Does anyone mention 'pay for' at all?"

2. **Depth 3-10 (Shallow threads)**:
   - Fast exploration of multiple subreddits
   - Looking for highly-upvoted discussions
   - Time-constrained searches
   - Example: "What are the top discussions about X?"

3. **Depth 32 (Balanced - Default)**:
   - Customer development research
   - Finding detailed pain points
   - Most use cases
   - Example: "What problems are people willing to pay to solve?"

4. **Depth None (Comprehensive)**:
   - Deep research into specific topics
   - Small, high-value subreddits
   - Following specific high-engagement threads
   - Example: "Get every comment from this 500-comment thread"

**Performance Impact Example**:
```
Searching r/SaaS with 100 posts, keyword "pay for":
- Depth 0:    ~500 comments,   ~2 minutes,  ~100 API requests
- Depth 10:   ~1,000 comments,  ~4 minutes,  ~150 API requests
- Depth 32:   ~1,500 comments,  ~6 minutes,  ~200 API requests
- Depth None: ~2,500 comments,  ~12 minutes, ~350 API requests
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
**Note**: This is now implemented in `config/sources/reddit.yaml` with expanded groups and presets (see section above).

**Subreddit Groups Included**:
- **Entrepreneurship**: SaaS, Entrepreneur, startups, smallbusiness, Bootstrapped, EntrepreneurRideAlong, SideProject
- **Product Development**: ProductManagement, userexperience, webdev, SomebodyMakeThis, AppIdeas, Lightbulb
- **B2B Business**: smallbusiness, Accounting, sales, marketing, freelance, consulting
- **Technical**: programming, webdev, selfhosted, sysadmin, devops

**Pre-configured Presets Included**:
- `saas_pain_points` - Find SaaS opportunities with payment signals
- `b2b_opportunities` - B2B workflow automation opportunities
- `developer_tools` - Developer tooling pain points
- `urgent_needs` - High-urgency unmet needs
- `competitive_intel` - Competitive pricing and switching behavior
- `productivity_pain` - Productivity and efficiency problems
- `feature_gaps` - Feature requests and product gaps

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Can search Reddit with configurable keywords and subreddits
- ✅ Scrapes posts and comments with rate limiting
- ✅ Stores data in SQLite with deduplication
- ✅ Resumes interrupted searches
- ✅ Generates HTML dashboard with basic charts
- ✅ Performs keyword frequency and sentiment analysis

### Full Feature Set
- ✅ All 5 analysis types working (frequency, clustering, sentiment, payment signals, context)
- ✅ Interactive Plotly visualizations
- ✅ CLI with all commands (search, report, list, resume, config, presets)
- ✅ Preset configuration system with 7+ pre-configured search patterns
- ✅ Subreddit groups for easy targeting
- ✅ Semantic search with configurable thresholds
- ✅ Dry-run mode with time/scope estimation
- ✅ Configurable comment depth
- ✅ Cross-search deduplication
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
- `config/sources/reddit.yaml` - Reddit subreddit groups and search presets
- `config/preset_loader.py` - PresetLoader class for managing presets

**Core Application**:
- `main.py` - CLI entry point with preset support
- `src/storage/models.py` - Database models (source-agnostic)
- `src/sources/base.py` - Plugin architecture base classes
- `src/sources/reddit/client.py` - Reddit plugin implementation
- `src/sources/reddit/parser.py` - Reddit comment tree parsing
- `src/core/rate_limiter.py` - Generic adaptive rate limiting
- `src/core/semantic_matcher.py` - Semantic similarity matching
- `src/core/search_engine.py` - Multi-source search orchestration
- `src/cli/commands.py` - CLI commands (search, report, presets, etc.)
- `src/cli/validators.py` - Input validation and dry-run estimation

**Analysis & Visualization**:
- `src/analysis/keyword_analyzer.py` - Frequency and trends
- `src/analysis/topic_clusterer.py` - ML clustering
- `src/analysis/sentiment_analyzer.py` - Sentiment analysis
- `src/analysis/payment_signal_analyzer.py` - Payment willingness detection
- `src/analysis/context_extractor.py` - Context extraction
- `src/visualization/dashboard.py` - Dashboard generator
- `src/visualization/charts.py` - Plotly charts
- `src/visualization/templates/report.html` - HTML template

**Documentation**:
- `README.md` - Update with usage guide and preset examples
- `CLAUDE.md` - Update with architecture details
