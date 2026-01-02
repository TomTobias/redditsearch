"""Shared pytest fixtures for testing

This module contains mock Reddit data that allows testing without API credentials.
"""
import pytest
from datetime import datetime, timezone


@pytest.fixture
def mock_reddit_posts():
    """Mock Reddit submission data for testing without API

    Returns realistic post data with payment signals, pain points,
    and various engagement levels for comprehensive testing.

    Returns:
        list: List of mock Reddit post dictionaries
    """
    return [
        {
            'id': 'abc123',
            'title': 'I would pay $50/month for a tool that automates invoicing',
            'selftext': 'Seriously, manually creating invoices takes me 2 hours per week. '
                       'I need a tool that integrates with my CRM and generates professional invoices automatically. '
                       'Would easily pay for this if it existed.',
            'author': 'entrepreneur_mike',
            'subreddit': 'SaaS',
            'score': 145,
            'num_comments': 23,
            'created_utc': datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc).timestamp(),
            'url': 'https://reddit.com/r/SaaS/comments/abc123',
        },
        {
            'id': 'def456',
            'title': 'Looking for a better project management tool',
            'selftext': 'Current tools like Jira are too complex. Need something simple for small teams. '
                       'Wish there was a tool that just focused on tasks without all the enterprise bloat.',
            'author': 'startup_founder',
            'subreddit': 'Entrepreneur',
            'score': 89,
            'num_comments': 15,
            'created_utc': datetime(2025, 1, 2, 10, 0, tzinfo=timezone.utc).timestamp(),
            'url': 'https://reddit.com/r/Entrepreneur/comments/def456',
        },
        {
            'id': 'ghi789',
            'title': 'Struggling with customer support emails',
            'selftext': 'We get 100+ support emails per day and manually categorizing them is killing us. '
                       'Need a tool to automatically tag and route emails to the right team members.',
            'author': 'saas_ceo',
            'subreddit': 'startups',
            'score': 234,
            'num_comments': 42,
            'created_utc': datetime(2025, 1, 3, 14, 30, tzinfo=timezone.utc).timestamp(),
            'url': 'https://reddit.com/r/startups/comments/ghi789',
        },
        {
            'id': 'jkl012',
            'title': 'Just launched our product!',
            'selftext': 'After 6 months of development, we finally launched. Check it out at myproduct.com',
            'author': 'product_launcher',
            'subreddit': 'SaaS',
            'score': 12,
            'num_comments': 3,
            'created_utc': datetime(2025, 1, 4, 9, 0, tzinfo=timezone.utc).timestamp(),
            'url': 'https://reddit.com/r/SaaS/comments/jkl012',
        },
    ]


@pytest.fixture
def mock_reddit_comments():
    """Mock Reddit comment data

    Returns comment data that can be linked to posts via parent_id.

    Returns:
        list: List of mock Reddit comment dictionaries
    """
    return [
        {
            'id': 'comment1',
            'body': 'I agree! I would pay for this too. Currently using spreadsheets and it is a nightmare.',
            'author': 'user123',
            'score': 34,
            'parent_id': 'abc123',  # Links to first post
            'created_utc': datetime(2025, 1, 1, 13, 0, tzinfo=timezone.utc).timestamp(),
        },
        {
            'id': 'comment2',
            'body': 'Have you tried QuickBooks? It does this but is expensive at $80/month.',
            'author': 'user456',
            'score': 12,
            'parent_id': 'abc123',
            'created_utc': datetime(2025, 1, 1, 14, 0, tzinfo=timezone.utc).timestamp(),
        },
        {
            'id': 'comment3',
            'body': 'We need a tool like this desperately. Willing to pay up to $100/month for our team.',
            'author': 'team_lead',
            'score': 45,
            'parent_id': 'abc123',
            'created_utc': datetime(2025, 1, 1, 15, 30, tzinfo=timezone.utc).timestamp(),
        },
        {
            'id': 'comment4',
            'body': 'Asana is pretty good for small teams. Worth checking out.',
            'author': 'helpful_user',
            'score': 8,
            'parent_id': 'def456',
            'created_utc': datetime(2025, 1, 2, 11, 0, tzinfo=timezone.utc).timestamp(),
        },
    ]


@pytest.fixture
def sample_keywords():
    """Common search keywords for testing

    Returns:
        list: List of keyword phrases commonly used in customer development
    """
    return [
        "pay for",
        "would pay",
        "need a tool",
        "wish there was",
        "struggling with",
        "desperately need",
    ]
