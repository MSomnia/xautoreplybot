"""Gemini-based reply generator."""

from __future__ import annotations

import time

from google import genai

USER_PROMPT_TEMPLATE = """以下是博主刚发布的推文，请以你的风格进行评论回复：

---
{tweet_text}
---

直接输出回复内容，不要任何前缀或解释。"""


class ReplyGenerationError(RuntimeError):
    """Raised when reply generation fails repeatedly."""


def generate_reply(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    tweet_text: str,
    max_attempts: int = 3,
    base_backoff_seconds: float = 1.0,
) -> str:
    client = genai.Client(api_key=api_key)
    user_prompt = USER_PROMPT_TEMPLATE.format(tweet_text=tweet_text)
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=model,
                config={"system_instruction": system_prompt},
                contents=user_prompt,
            )
            text = (response.text or "").strip()
            if text:
                return text
            raise ReplyGenerationError("Gemini returned empty response text")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == max_attempts - 1:
                break
            time.sleep(base_backoff_seconds * (2**attempt))

    raise ReplyGenerationError(f"Failed to generate reply after {max_attempts} attempts: {last_error}")
