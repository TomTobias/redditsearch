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
│   └── subreddits.yaml             # Default subreddit groups
├── src/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py             # Click commands
│   │   └── validators.py           # Input validation
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── reddit_client.py        # PRAW wrapper
│   │   ├── search_engine.py        # Search orchestration
│   │   ├── comment_parser.py       # Comment tree traversal
│   │   └── rate_limiter.py         # Adaptive rate limiting
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── models.py               # SQLAlchemy ORM
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
    ├── test_scraper.py
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

### Database Schema

**Core Tables**:

1. **searches** - Track each search operation
   - Fields: search_id (UUID), keywords (JSON), subreddits (JSON), time_filter, min_score, status, timestamps
   - Purpose: Resume capability, search history

2. **submissions** - Reddit posts/threads
   - Fields: reddit_id (unique), title, body, author, subreddit, url, score, num_comments, created_utc
   - Deduplication: `reddit_id` unique constraint, `first_seen_search_id`, `seen_count`
   - Indexes: (created_utc, score), (subreddit, created_utc)

3. **comments** - Reddit comments
   - Fields: reddit_id (unique), submission_id (FK), parent_id (threading), body, author, score, depth
   - Indexes: (submission_id, depth) for tree queries

4. **keyword_matches** - Where keywords found with context
   - Fields: search_id (FK), keyword, submission_id/comment_id (FKs), match_type, context_before, matched_text, context_after, full_paragraph
   - Purpose: Store extracted context for analysis
   - Indexes: (keyword, search_id)

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
# Search Reddit
redditsearch search \
  --keywords "pay for,wish there was,need a tool" \
  --subreddits "SaaS,Entrepreneur,startups" \
  --days 30 \
  --min-score 5 \
  --max-posts 100

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
- Update `pyproject.toml` with all dependencies
- Create `config/settings.py` with Pydantic settings
- Create `config/subreddits.yaml` with default lists
- Create `.env.example` template
- Setup `src/` package structure
- Implement `src/utils/logger.py`

**Git checkpoint**:
```bash
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

**Git checkpoint**:
```bash
git add .
git commit -m "Phase 2: Database models and migrations"
git push origin main
```

### Phase 3: Reddit Scraper
**Files to create**:
- `src/scraper/rate_limiter.py` - Adaptive rate limiting class
- `src/scraper/reddit_client.py` - PRAW wrapper with rate limiting
- `src/scraper/comment_parser.py` - Comment tree traversal logic
- `src/scraper/search_engine.py` - Orchestrates searches, handles keywords, saves to DB
- `src/utils/state_manager.py` - State tracking for resume

**Git checkpoint**:
```bash
git add .
git commit -m "Phase 3: Reddit scraper with rate limiting"
git push origin main
```

### Phase 4: CLI Interface
**Files to create**:
- Update `main.py` - Entry point with Click app
- `src/cli/commands.py` - Command implementations (search, report, list, resume)
- `src/cli/validators.py` - Input validation helpers

**Git checkpoint**:
```bash
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

**Git checkpoint**:
```bash
git add .
git commit -m "Phase 5: Analysis pipeline (NLP and ML)"
git push origin main
```

### Phase 6: Visualization
**Files to create**:
- `src/visualization/charts.py` - Plotly chart builders
- `src/visualization/templates/report.html` - Jinja2 HTML template
- `src/visualization/dashboard.py` - Dashboard generator (runs analyses, builds charts, renders HTML)

**Git checkpoint**:
```bash
git add .
git commit -m "Phase 6: Interactive visualizations and dashboards"
git push origin main
```

### Phase 7: Testing & Documentation
**Files to create**:
- `tests/test_scraper.py` - Test Reddit client, rate limiter
- `tests/test_storage.py` - Test models, repositories
- `tests/test_analysis.py` - Test analysis modules
- Update `README.md` - Usage guide, setup instructions
- Update `CLAUDE.md` - Development guide

**Git checkpoint**:
```bash
git add .
git commit -m "Phase 7: Tests and documentation complete"
git push origin main
```

## Critical Implementation Details

### 1. Reddit API Setup
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
