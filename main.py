"""Single-run entrypoint for GitHub Actions."""

from __future__ import annotations

import logging

from config import load_settings
from fetcher import get_new_tweets
from filter import ValidationError, validate_reply
from generator import ReplyGenerationError, generate_reply
from replier import ReplySendError, send_reply
from state import load_state, save_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run() -> None:
    settings = load_settings()
    state = load_state()

    tweets = get_new_tweets(
        bearer_token=settings.x_bearer_token,
        user_id=settings.x_main_user_id,
        since_id=state.since_id,
    )
    if not tweets:
        logger.info("No new tweets found")
        state.mark_run()
        save_state(state)
        return

    logger.info("Fetched %s new tweets", len(tweets))

    for tweet in tweets:
        logger.info("Processing tweet %s", tweet.id)
        latest_valid_reply: str | None = None

        for _ in range(settings.max_filter_attempts):
            try:
                candidate = generate_reply(
                    api_key=settings.grok_api_key,
                    model=settings.grok_model,
                    base_url=settings.grok_base_url,
                    system_prompt=settings.bot_system_prompt,
                    tweet_text=tweet.text,
                    max_attempts=settings.max_generate_attempts,
                )
                validate_reply(
                    candidate,
                    max_chars=settings.max_reply_chars,
                    recent_replies=[item.reply_text for item in state.recent_replies],
                )
                latest_valid_reply = candidate
                break
            except (ReplyGenerationError, ValidationError) as exc:
                logger.warning("Reply attempt failed for tweet %s: %s", tweet.id, exc)

        if latest_valid_reply is None:
            logger.error("Skip tweet %s because no valid reply generated", tweet.id)
            state.since_id = tweet.id
            continue

        try:
            sent_id = send_reply(
                api_key=settings.x_api_key,
                api_secret=settings.x_api_secret,
                access_token=settings.x_access_token,
                access_token_secret=settings.x_access_token_secret,
                tweet_id=tweet.id,
                text=latest_valid_reply,
            )
            logger.info("Reply sent for tweet %s with reply id %s", tweet.id, sent_id)
            state.add_reply(tweet.id, latest_valid_reply, keep_last=settings.recent_reply_window)
            state.since_id = tweet.id
        except ReplySendError as exc:
            logger.error("Failed to send reply for tweet %s: %s", tweet.id, exc)

    state.mark_run()
    save_state(state)


if __name__ == "__main__":
    run()
