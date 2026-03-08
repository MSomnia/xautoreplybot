"""Content checks for generated replies."""

from __future__ import annotations

from difflib import SequenceMatcher

SENSITIVE_KEYWORDS = [
    "政治",
]


class ValidationError(RuntimeError):
    """Raised when generated content does not pass safety checks."""


def _is_too_similar(text: str, previous: list[str], threshold: float = 0.9) -> bool:
    for old in previous:
        similarity = SequenceMatcher(None, text, old).ratio()
        if similarity >= threshold:
            return True
    return False


def validate_reply(
    reply: str,
    *,
    max_chars: int,
    recent_replies: list[str],
    sensitive_keywords: list[str] | None = None,
) -> None:
    if not reply.strip():
        raise ValidationError("reply is empty")

    if len(reply) > max_chars:
        raise ValidationError(f"reply exceeds max length: {len(reply)} > {max_chars}")

    keyword_list = sensitive_keywords or SENSITIVE_KEYWORDS
    lowered = reply.lower()
    if any(keyword.lower() in lowered for keyword in keyword_list):
        raise ValidationError("reply contains sensitive keyword")

    if _is_too_similar(reply, recent_replies):
        raise ValidationError("reply is too similar to recent outputs")
