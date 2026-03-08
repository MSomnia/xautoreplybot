"""Fetch latest tweets from the main account."""

from __future__ import annotations

from dataclasses import dataclass

import tweepy


@dataclass
class Tweet:
    id: str
    text: str
    context_text: str
    created_at: str | None


def get_new_tweets(*, bearer_token: str, user_id: str, since_id: str | None) -> list[Tweet]:
    """Return new tweets ordered from oldest to newest."""
    client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

    response = client.get_users_tweets(
        id=user_id,
        since_id=since_id,
        max_results=10,
        tweet_fields=["created_at", "conversation_id", "referenced_tweets"],
        expansions=["referenced_tweets.id"],
    )

    tweets = response.data or []
    includes = response.includes or {}
    referenced_tweets = includes.get("tweets", [])
    referenced_map = {str(item.id): item for item in referenced_tweets}

    def _ref_id(ref: object) -> str | None:
        if hasattr(ref, "id"):
            return str(getattr(ref, "id"))
        if isinstance(ref, dict):
            val = ref.get("id")
            return str(val) if val is not None else None
        return None

    def _ref_type(ref: object) -> str | None:
        if hasattr(ref, "type"):
            return str(getattr(ref, "type"))
        if isinstance(ref, dict):
            val = ref.get("type")
            return str(val) if val is not None else None
        return None

    def _build_context_text(item: object) -> str:
        base_text = str(getattr(item, "text", "") or "").strip()
        refs = getattr(item, "referenced_tweets", None) or []
        related_parts: list[str] = []
        for ref in refs:
            ref_type = _ref_type(ref)
            if ref_type not in {"quoted", "retweeted", "replied_to"}:
                continue
            rid = _ref_id(ref)
            if not rid:
                continue
            source = referenced_map.get(rid)
            if not source:
                continue
            source_text = str(getattr(source, "text", "") or "").strip()
            if not source_text:
                continue
            related_parts.append(f"[{ref_type}] {source_text}")

        if not related_parts:
            return base_text
        return f"{base_text}\n\n以下是该帖关联原文上下文：\n" + "\n".join(related_parts)

    items = [
        Tweet(
            id=str(t.id),
            text=t.text,
            context_text=_build_context_text(t),
            created_at=t.created_at.isoformat() if t.created_at else None,
        )
        for t in tweets
    ]
    items.sort(key=lambda t: int(t.id))
    return items
