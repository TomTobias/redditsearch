# Reddit Customer Development Tool - Implementation Plan

## Overview

Build a Python 3.14 application to search Reddit for customer pain points and market opportunities. This plan uses a **foundational-first approach** - start simple, build incrementally, add advanced features only after core functionality works.

## Project Goals

- **Primary**: Find pain points that represent app opportunities for solopreneurs
- **Search for**: Keywords like "pay for", "wish there was", "need a tool", "struggling with"
- **Target**: Subreddits like r/SaaS, r/Entrepreneur, r/startups, r/smallbusiness
- **Output**: Searchable database + CSV/JSON exports (visualization optional later)

---

## Implementation Phases

### PHASE 1: Core Foundation (Simple)
**Goal**: Set up project structure, minimal dependencies, and mock data for testing without Reddit credentials.

**Duration Estimate**: 1-2 hours

**Files to Create**:
```
src/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py              # Basic Pydantic settings
└── utils/
    ├── __init__.py
    └── logger.py                 # Simple logging setup

tests/
├── __init__.py
├── conftest.py                   # Mock Reddit data fixtures
└── test_config.py                # Test settings loading

.env.example                      # Credential template
pytest.ini                        # Pytest configuration
pyproject.toml                    # Update with minimal dependencies
```

**Dependencies to Add**:
```toml
dependencies = [
    "pydantic>=2.5.0",           # Settings validation
    "pydantic-settings>=2.1.0",  # Settings from env vars
    "python-dotenv>=1.0.0",      # Load .env files
    "click>=8.1.0",              # CLI framework
    "rich>=13.7.0",              # Pretty terminal output
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",             # Testing framework
    "pytest-cov>=4.1.0",         # Code coverage
    "pytest-mock>=3.12.0",       # Mocking support
    "black>=23.12.0",            # Code formatter
    "ruff>=0.1.0",               # Fast linter
]
```

**Key Implementation**: Mock Reddit data in `tests/conftest.py`:
```python
@pytest.fixture
def mock_reddit_posts():
    """Mock Reddit submission data for testing without API"""
    return [
        {
            'id': 'abc123',
            'title': 'I would pay $50/month for a tool that automates invoicing',
            'selftext': 'Seriously, manually creating invoices takes me 2 hours per week...',
            'author': 'entrepreneur_mike',
            'subreddit': 'SaaS',
            'score': 145,
            'num_comments': 23,
            'created_utc': 1704110400.0,
            'url': 'https://reddit.com/r/SaaS/comments/abc123',
        },
        # More mock posts...
    ]
```

**Testing**:
- Test settings load from .env and defaults
- Test mock data fixtures are available
- Run: `pytest tests/test_config.py -v`

**Success Criteria**:
- ✅ `pytest` runs and passes
- ✅ Settings load from .env (if present) or use defaults
- ✅ Mock data fixtures available for next phases
- ✅ Project structure established

**Git Checkpoint**:
```bash
pytest tests/test_config.py -v
git add .
git commit -m "Phase 1: Core foundation with mock data and basic config"
git push origin main
```

---

### PHASE 2: Basic Search (Moderate)
**Goal**: Implement simplest possible keyword search using exact string matching. Use mock data initially, support real PRAW later.

**Duration Estimate**: 3-4 hours

**Files to Create**:
```
src/
├── search/
│   ├── __init__.py
│   ├── reddit_client.py         # PRAW wrapper with mock support
│   └── keyword_matcher.py       # Simple case-insensitive string search
└── models/
    ├── __init__.py
    └── search_models.py         # Pydantic models for posts, comments

tests/
├── test_reddit_client.py        # Test with mock data
└── test_keyword_matcher.py      # Test exact keyword matching
```

**Dependencies to Add**:
```toml
dependencies = [
    # ... Phase 1 deps ...
    "praw>=7.7.1",               # Reddit API wrapper
]
```

**Key Implementation**: Reddit client with mock fallback:
```python
class RedditClient:
    def __init__(self, client_id="", client_secret="", user_agent="", use_mock=True):
        self.use_mock = use_mock
        if not use_mock and client_id:
            self.reddit = praw.Reddit(...)
        else:
            self.reddit = None
            self.mock_data = []

    def search_subreddit(self, subreddit, query, limit=100):
        if self.use_mock:
            return [p for p in self.mock_data['posts']
                    if p['subreddit'].lower() == subreddit.lower()][:limit]
        else:
            # Real PRAW API call
            ...
```

**Testing**:
- Test RedditClient with mock data (no API)
- Test KeywordMatcher with sample text
- Test case-insensitive matching
- Test context extraction
- Run: `pytest tests/test_reddit_client.py tests/test_keyword_matcher.py -v`

**Success Criteria**:
- ✅ Can search mock Reddit posts for exact keywords
- ✅ Extracts context around matches
- ✅ Works entirely offline with mock data
- ✅ Can switch to real PRAW by setting `use_mock=False`

**Git Checkpoint**:
```bash
pytest tests/test_reddit_client.py tests/test_keyword_matcher.py -v
git add .
git commit -m "Phase 2: Basic keyword search with mock Reddit data"
git push origin main
```

---

### PHASE 3: CLI & Output (Moderate)
**Goal**: Add Click-based CLI and export results to CSV/JSON files.

**Duration Estimate**: 2-3 hours

**Files to Create**:
```
src/
├── cli/
│   ├── __init__.py
│   └── commands.py              # Click commands
└── output/
    ├── __init__.py
    └── exporters.py             # CSV and JSON exporters

main.py                          # Update with Click app
tests/
├── test_cli.py                  # Test CLI commands
└── test_exporters.py            # Test output generation
```

**No New Dependencies** (Click and Rich already added in Phase 1)

**Key Implementation**: CLI search command:
```python
@click.command()
@click.option('--keywords', '-k', required=True)
@click.option('--subreddits', '-s')
@click.option('--output', '-o', help='Output file (.csv or .json)')
@click.option('--mock/--no-mock', default=True)
def search(keywords, subreddits, output, mock):
    # Parse inputs
    # Search using RedditClient and KeywordMatcher
    # Display Rich table
    # Export to CSV/JSON if requested
```

**Testing**:
- Test CLI with Click's CliRunner
- Test CSV export
- Test JSON export
- Run: `pytest tests/test_cli.py tests/test_exporters.py -v`

**Success Criteria**:
- ✅ Can run `python main.py search --keywords "pay for" --output results.csv --mock`
- ✅ Results display in terminal as formatted table
- ✅ CSV/JSON files created with correct data
- ✅ Works with mock data (no API required)

**Git Checkpoint**:
```bash
pytest tests/test_cli.py tests/test_exporters.py -v
git add .
git commit -m "Phase 3: CLI interface and CSV/JSON export"
git push origin main
```

---

### PHASE 4: Database & Persistence (Moderate)
**Goal**: Add SQLite database with SQLAlchemy for storing searches, posts, and matches.

**Duration Estimate**: 3-4 hours

**Files to Create**:
```
src/
└── storage/
    ├── __init__.py
    ├── models.py                # SQLAlchemy ORM models
    ├── database.py              # Database connection
    └── repositories.py          # Repository pattern

tests/
└── test_storage.py              # Test database operations
```

**Dependencies to Add**:
```toml
dependencies = [
    # ... Phase 1-3 deps ...
    "sqlalchemy>=2.0.0",         # ORM
    "alembic>=1.13.0",           # Database migrations
]
```

**Key Implementation**: Database models:
```python
class Search(Base):
    __tablename__ = "searches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keywords: Mapped[str] = mapped_column(JSON)
    subreddits: Mapped[str] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    post_count: Mapped[int] = mapped_column(Integer)

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reddit_id: Mapped[str] = mapped_column(String(50), unique=True)  # For deduplication
    search_id: Mapped[int] = mapped_column(ForeignKey("searches.id"))
    title: Mapped[str] = mapped_column(Text)
    # ... more fields
```

**Testing**:
- Test model creation and relationships
- Test repository CRUD operations
- Test deduplication (same post added twice)
- Use in-memory SQLite for tests
- Run: `pytest tests/test_storage.py -v`

**Success Criteria**:
- ✅ Searches saved to SQLite database
- ✅ Posts deduplicated by reddit_id
- ✅ Keyword matches linked to posts
- ✅ Can query historical searches
- ✅ Database at `data/redditsearch.db`

**Git Checkpoint**:
```bash
pytest tests/test_storage.py -v
git add .
git commit -m "Phase 4: SQLite database with SQLAlchemy"
git push origin main
```

---

### PHASE 5: Testing & Validation (Simple)
**Goal**: Comprehensive test coverage and validation with real Reddit API (when credentials available).

**Duration Estimate**: 2-3 hours

**Files to Create**:
```
tests/
├── test_integration.py          # End-to-end tests
└── test_real_api.py             # Real Reddit API tests

docs/
└── TESTING.md                   # How to get credentials
```

**No New Dependencies** (all testing deps added in Phase 1)

**Key Implementation**: Real API tests (skip if no credentials):
```python
@pytest.mark.skipif(
    not get_settings().REDDIT_CLIENT_ID,
    reason="Requires Reddit API credentials in .env"
)
def test_real_reddit_api():
    client = RedditClient(use_mock=False)
    results = client.search_subreddit('SaaS', 'pricing', limit=5)
    assert len(results) > 0
```

**Testing**:
- Run all Phase 1-4 tests
- Add integration tests
- Add real API tests (marked to skip)
- Measure coverage
- Run: `pytest tests/ --cov=src --cov-report=html`

**Success Criteria**:
- ✅ All tests pass with mock data
- ✅ Real API tests work with credentials
- ✅ Test coverage >80%
- ✅ Documentation for Reddit API setup
- ✅ Can validate with real Reddit API

**Git Checkpoint**:
```bash
pytest tests/ --cov=src --cov-report=html
git add .
git commit -m "Phase 5: Comprehensive testing and validation"
git push origin main
```

---

## MVP Complete After Phase 5

After Phase 5, you have a **fully functional Reddit search tool**:

✅ Search Reddit for keywords (with mocks or real API)
✅ Exact keyword matching with context extraction
✅ Results saved to SQLite database
✅ Export to CSV and JSON
✅ CLI interface with Rich formatting
✅ Full test coverage (>80%)
✅ Works offline with mock data
✅ Ready for real Reddit API when credentials available

**Total Development Time**: ~13-18 hours

---

## PHASE 6+: Advanced Features (Add as Needed)

After Phase 5, add features incrementally based on priority:

| Phase | Feature | Complexity | Dependencies | Description |
|-------|---------|------------|--------------|-------------|
| 6A | Basic Visualization | Complex | plotly, jinja2 | Interactive HTML dashboards with charts |
| 6B | Payment Signal Analyzer | Moderate | None | Detect "would pay $X", "worth $Y/month" |
| 6C | Sentiment (VADER) | Simple | vaderSentiment | Lightweight sentiment analysis (no ML) |
| 6D | Preset Configurations | Simple | None | Save common search patterns |
| 6E | Semantic Search | Complex | sentence-transformers | Find similar phrases using embeddings (~500MB) |
| 6F | Plugin Architecture | Complex | None | Abstract source interface for multi-platform |
| 6G | Topic Clustering | Complex | scikit-learn | Group posts into topics using ML |
| 6H | URL Type Filtering | Simple | None | Filter by self-posts vs link posts |
| 6I | Spam/Hype Detection | Moderate | None | Filter promotional content |

**Recommended Order After Phase 5**:
1. **Phase 6B**: Payment Signal Analyzer - directly supports customer development
2. **Phase 6C**: Sentiment (VADER) - lightweight, valuable insights
3. **Phase 6A**: Basic Visualization - makes data more accessible
4. User decides remaining features based on actual usage

---

## Critical Files

The 5 most important files that everything else depends on:

1. [src/config/settings.py](src/config/settings.py) - Core configuration
2. [src/search/reddit_client.py](src/search/reddit_client.py) - Reddit API abstraction with mock support
3. [src/search/keyword_matcher.py](src/search/keyword_matcher.py) - Core keyword matching logic
4. [src/storage/models.py](src/storage/models.py) - Database schema
5. [tests/conftest.py](tests/conftest.py) - Mock data fixtures

---

## Implementation Principles

1. **Work Incrementally** - Each phase delivers working functionality
2. **Test Early** - Tests written alongside code, not after
3. **Mock First** - Develop without API credentials, validate later
4. **Simple Before Complex** - Exact matching before ML
5. **Git Checkpoints** - Commit after each phase passes tests
6. **User Choice** - You decide Phase 6+ order and priority

---

## Development Workflow Per Phase

1. Create files and directory structure
2. Add dependencies to pyproject.toml
3. Implement core functionality
4. Write tests (aim for >80% coverage)
5. Run tests until all pass
6. Git commit with descriptive message
7. Ask user if ready to proceed to next phase

---

## Reddit API Credentials

### When Needed
- **Not required for Phases 1-5** - Everything works with mock data
- **Optional for validation** - Get credentials from https://www.reddit.com/prefs/apps
- **Test with `test_real_api.py`** - Validates mock behavior matches reality

### How to Get Credentials
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app"
3. Select "script" type
4. Fill in name and redirect URI (http://localhost:8080)
5. Copy client ID and secret to `.env`:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=redditsearch/0.1.0 by your_username
```

---

## Key Changes from Original Plan

This reorganized plan differs from the original 3,992-line plan:

| Aspect | Original Plan | Reorganized Plan |
|--------|---------------|------------------|
| **Phase 1** | All 28+ dependencies at once | 5 minimal dependencies |
| **Phase 3** | Semantic search + plugin architecture | Simple exact string matching |
| **Phase 5** | Payment signals + ML clustering | Just keyword frequency |
| **Sentiment** | Transformers (2GB+) from start | Deferred, use VADER when added |
| **Testing** | One phase at end | Every phase has tests |
| **API Access** | Assumes credentials available | Mock-first, API optional |
| **Complexity** | 7 advanced features in initial phases | 5 phases to MVP, then features |
| **Approach** | Big bang implementation | Incremental, testable milestones |

---

## Next Steps

Ready to start? Here's the path forward:

1. ✅ **Plan approved** - This document
2. **Start Phase 1** - Core foundation (1-2 hours)
3. **Proceed incrementally** - One phase at a time
4. **Validate each phase** - Tests pass before moving forward
5. **Reach MVP** (Phase 5) - Fully functional tool
6. **Add features** - User-driven priority

**Goal**: Get something working fast (5 phases), then add sophistication incrementally and controllably.
