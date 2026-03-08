"""Send replies via X API."""

from __future__ import annotations

import time

import tweepy


class ReplySendError(RuntimeError):
    """Raised when sending a reply fails repeatedly."""


def _build_client(api_key: str, api_secret: str, access_token: str, access_token_secret: str) -> tweepy.Client:
    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=False,
    )


def send_reply(
    *,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
    tweet_id: str,
    text: str,
    max_attempts: int = 3,
) -> str:
    client = _build_client(api_key, api_secret, access_token, access_token_secret)
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            response = client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
            if response.data and response.data.get("id"):
                return str(response.data["id"])
            raise ReplySendError("X API returned no reply tweet id")
        except tweepy.TooManyRequests as exc:
            last_error = exc
            wait_seconds = 60 * (attempt + 1)
            time.sleep(wait_seconds)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < max_attempts - 1:
                time.sleep(2**attempt)

    raise ReplySendError(f"Failed to send reply after {max_attempts} attempts: {last_error}")
