"""State persistence for bot runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_FILE = Path("state.json")


@dataclass
class ReplyRecord:
    tweet_id: str
    reply_text: str
    time: str


@dataclass
class BotState:
    since_id: str | None = None
    last_run: str | None = None
    recent_replies: list[ReplyRecord] = field(default_factory=list)

    def add_reply(self, tweet_id: str, reply_text: str, keep_last: int = 20) -> None:
        record = ReplyRecord(
            tweet_id=tweet_id,
            reply_text=reply_text,
            time=datetime.now(timezone.utc).isoformat(),
        )
        self.recent_replies.append(record)
        if keep_last > 0 and len(self.recent_replies) > keep_last:
            self.recent_replies = self.recent_replies[-keep_last:]

    def mark_run(self) -> None:
        self.last_run = datetime.now(timezone.utc).isoformat()


DEFAULT_STATE = BotState(since_id=None, last_run=None, recent_replies=[])


def load_state(path: Path = STATE_FILE) -> BotState:
    if not path.exists():
        return BotState()

    with path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = json.load(f)

    replies = [ReplyRecord(**item) for item in raw.get("recent_replies", [])]
    return BotState(
        since_id=raw.get("since_id"),
        last_run=raw.get("last_run"),
        recent_replies=replies,
    )


def save_state(state: BotState, path: Path = STATE_FILE) -> None:
    payload = {
        "since_id": state.since_id,
        "last_run": state.last_run,
        "recent_replies": [asdict(item) for item in state.recent_replies],
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
