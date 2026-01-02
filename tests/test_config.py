"""Tests for configuration and settings"""
import pytest
from src.config.settings import Settings, get_settings


def test_settings_defaults():
    """Test that settings load with default values"""
    settings = Settings()

    # Check defaults are set correctly
    assert settings.REDDIT_CLIENT_ID == ""
    assert settings.REDDIT_CLIENT_SECRET == ""
    assert settings.REDDIT_USER_AGENT == "redditsearch/0.1.0"
    assert settings.DEFAULT_SUBREDDITS == ["SaaS", "Entrepreneur", "startups"]
    assert settings.DEFAULT_KEYWORDS == ["pay for", "need a tool", "wish there was"]
    assert settings.DATABASE_PATH == "data/redditsearch.db"
    assert settings.OUTPUT_DIR == "output"


def test_get_settings():
    """Test the get_settings helper function"""
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.DEFAULT_SUBREDDITS is not None


def test_settings_with_env_override(monkeypatch):
    """Test that environment variables override defaults"""
    # Set environment variables
    monkeypatch.setenv("REDDIT_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "test_secret")
    monkeypatch.setenv("DATABASE_PATH", "custom/path/db.sqlite")

    settings = Settings()

    # Check overrides work
    assert settings.REDDIT_CLIENT_ID == "test_client_id"
    assert settings.REDDIT_CLIENT_SECRET == "test_secret"
    assert settings.DATABASE_PATH == "custom/path/db.sqlite"

    # Check other defaults still intact
    assert settings.DEFAULT_SUBREDDITS == ["SaaS", "Entrepreneur", "startups"]


def test_mock_reddit_posts_fixture(mock_reddit_posts):
    """Test that mock Reddit posts fixture is available"""
    assert isinstance(mock_reddit_posts, list)
    assert len(mock_reddit_posts) > 0

    # Check first post has required fields
    first_post = mock_reddit_posts[0]
    assert 'id' in first_post
    assert 'title' in first_post
    assert 'selftext' in first_post
    assert 'author' in first_post
    assert 'subreddit' in first_post
    assert 'score' in first_post
    assert 'num_comments' in first_post
    assert 'created_utc' in first_post
    assert 'url' in first_post


def test_mock_reddit_comments_fixture(mock_reddit_comments):
    """Test that mock Reddit comments fixture is available"""
    assert isinstance(mock_reddit_comments, list)
    assert len(mock_reddit_comments) > 0

    # Check first comment has required fields
    first_comment = mock_reddit_comments[0]
    assert 'id' in first_comment
    assert 'body' in first_comment
    assert 'author' in first_comment
    assert 'score' in first_comment
    assert 'parent_id' in first_comment
    assert 'created_utc' in first_comment


def test_sample_keywords_fixture(sample_keywords):
    """Test that sample keywords fixture is available"""
    assert isinstance(sample_keywords, list)
    assert len(sample_keywords) > 0
    assert "pay for" in sample_keywords
    assert "need a tool" in sample_keywords


def test_mock_data_has_payment_signals(mock_reddit_posts):
    """Test that mock data contains payment signals for testing"""
    # Check that at least one post has payment signals
    texts = [p['title'] + ' ' + p['selftext'] for p in mock_reddit_posts]
    combined_text = ' '.join(texts).lower()

    # Should find payment-related phrases
    assert 'pay' in combined_text or 'would pay' in combined_text
    assert '$' in combined_text  # Dollar amounts


def test_mock_data_has_pain_points(mock_reddit_posts):
    """Test that mock data contains pain point language"""
    texts = [p['title'] + ' ' + p['selftext'] for p in mock_reddit_posts]
    combined_text = ' '.join(texts).lower()

    # Should find pain point phrases
    pain_indicators = ['need', 'struggling', 'wish', 'looking for']
    assert any(indicator in combined_text for indicator in pain_indicators)
