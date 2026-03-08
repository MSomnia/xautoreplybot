"""Fetch latest tweets from the main account."""

from __future__ import annotations

from dataclasses import dataclass

import tweepy


@dataclass
class Tweet:
    id: str
    text: str
    created_at: str | None


def get_new_tweets(*, bearer_token: str, user_id: str, since_id: str | None) -> list[Tweet]:
    """Return new tweets ordered from oldest to newest."""
    client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

    response = client.get_users_tweets(
        id=user_id,
        since_id=since_id,
        max_results=10,
        tweet_fields=["created_at", "conversation_id"],
        exclude=["retweets", "replies"],
    )

    tweets = response.data or []
    items = [
        Tweet(id=t.id, text=t.text, created_at=t.created_at.isoformat() if t.created_at else None)
        for t in tweets
    ]
    items.sort(key=lambda t: int(t.id))
    return items
