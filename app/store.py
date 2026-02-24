from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal, Protocol
from uuid import uuid4

from app.schemas import InterestSignal, ObservedError, SessionPlan, SessionTurn

Outcome = Literal["success", "fail", "hinted"]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Item:
    id: str
    learner_id: str
    item_type: str
    prompt_form: str
    target_form: str


@dataclass
class ItemState:
    item_id: str
    learner_id: str
    ease: float = 2.5
    reps: int = 0
    lapses: int = 0
    next_due_at: datetime = field(default_factory=utcnow)


class Store(Protocol):
    def create_item(self, learner_id: str, item_type: str, prompt_form: str, target_form: str) -> Item: ...
    def due_items(self, learner_id: str, now: datetime, limit: int = 12) -> list[dict]: ...
    def apply_review(self, learner_id: str, item_id: str, outcome: Outcome, confidence: float | None = None) -> ItemState: ...
    def has_item(self, item_id: str) -> bool: ...
    def create_session(self, session_id: str, plan: SessionPlan) -> None: ...
    def complete_session(self, session_id: str, outcomes: dict) -> None: ...
    def insert_turns(self, session_id: str, turns: list[SessionTurn]) -> None: ...
    def insert_errors(self, learner_id: str, session_id: str, errors: list[ObservedError]) -> None: ...
    def upsert_interests(self, learner_id: str, signals: list[InterestSignal]) -> None: ...


class SQLiteStore:
    def __init__(self, db_path: str = "data/languageapp.db") -> None:
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS items (
                  id TEXT PRIMARY KEY,
                  learner_id TEXT NOT NULL,
                  item_type TEXT NOT NULL,
                  prompt_form TEXT NOT NULL,
                  target_form TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS item_state (
                  item_id TEXT PRIMARY KEY,
                  learner_id TEXT NOT NULL,
                  ease REAL NOT NULL,
                  reps INTEGER NOT NULL,
                  lapses INTEGER NOT NULL,
                  next_due_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS item_reviews (
                  id TEXT PRIMARY KEY,
                  learner_id TEXT NOT NULL,
                  item_id TEXT NOT NULL,
                  outcome TEXT NOT NULL,
                  score REAL NOT NULL,
                  reviewed_at TEXT NOT NULL,
                  FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS sessions (
                  id TEXT PRIMARY KEY,
                  learner_id TEXT NOT NULL,
                  topic TEXT,
                  started_at TEXT NOT NULL,
                  ended_at TEXT,
                  plan_json TEXT NOT NULL,
                  outcomes_json TEXT
                );
                CREATE TABLE IF NOT EXISTS session_turns (
                  id TEXT PRIMARY KEY,
                  session_id TEXT NOT NULL,
                  turn_index INTEGER NOT NULL,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  latency_ms INTEGER,
                  created_at TEXT NOT NULL,
                  UNIQUE(session_id, turn_index)
                );
                CREATE TABLE IF NOT EXISTS errors (
                  id TEXT PRIMARY KEY,
                  learner_id TEXT NOT NULL,
                  session_id TEXT,
                  category TEXT NOT NULL,
                  learner_text TEXT NOT NULL,
                  corrected_text TEXT NOT NULL,
                  explanation TEXT,
                  created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS interests (
                  id TEXT PRIMARY KEY,
                  learner_id TEXT NOT NULL,
                  topic TEXT NOT NULL,
                  weight REAL NOT NULL,
                  mention_count INTEGER NOT NULL,
                  last_seen_at TEXT,
                  updated_at TEXT NOT NULL,
                  UNIQUE(learner_id, topic)
                );
                """
            )
            self.conn.commit()

    def create_item(self, learner_id: str, item_type: str, prompt_form: str, target_form: str) -> Item:
        item = Item(id=str(uuid4()), learner_id=learner_id, item_type=item_type, prompt_form=prompt_form, target_form=target_form)
        now = utcnow().isoformat()
        with self._lock:
            self.conn.execute(
                "INSERT INTO items (id, learner_id, item_type, prompt_form, target_form, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (item.id, learner_id, item_type, prompt_form, target_form, now),
            )
            self.conn.execute(
                "INSERT INTO item_state (item_id, learner_id, ease, reps, lapses, next_due_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (item.id, learner_id, 2.5, 0, 0, now, now),
            )
            self.conn.commit()
        return item

    def due_items(self, learner_id: str, now: datetime, limit: int = 12) -> list[dict]:
        with self._lock:
            rows = self.conn.execute(
                """
                SELECT i.id, i.item_type, i.prompt_form, i.target_form,
                       s.learner_id, s.ease, s.reps, s.lapses, s.next_due_at
                FROM item_state s
                JOIN items i ON i.id = s.item_id
                WHERE s.learner_id = ? AND s.next_due_at <= ?
                ORDER BY s.next_due_at ASC
                LIMIT ?
                """,
                (learner_id, now.isoformat(), limit),
            ).fetchall()
        return [
            {
                "item": Item(row["id"], row["learner_id"], row["item_type"], row["prompt_form"], row["target_form"]),
                "state": ItemState(
                    item_id=row["id"],
                    learner_id=row["learner_id"],
                    ease=row["ease"],
                    reps=row["reps"],
                    lapses=row["lapses"],
                    next_due_at=datetime.fromisoformat(row["next_due_at"]),
                ),
            }
            for row in rows
        ]

    def apply_review(self, learner_id: str, item_id: str, outcome: Outcome, confidence: float | None = None) -> ItemState:
        with self._lock:
            row = self.conn.execute(
                "SELECT learner_id, ease, reps, lapses, next_due_at FROM item_state WHERE item_id = ?", (item_id,)
            ).fetchone()
            if row is None:
                raise ValueError(f"Unknown item_id: {item_id}")
            state = ItemState(item_id, row["learner_id"], row["ease"], row["reps"], row["lapses"], datetime.fromisoformat(row["next_due_at"]))
            if state.learner_id != learner_id:
                raise ValueError(f"Item {item_id} does not belong to learner {learner_id}")

            score = {"success": 4.0, "hinted": 2.5, "fail": 1.0}[outcome]
            if confidence is not None:
                score = max(0.0, min(5.0, score + (confidence - 0.5)))

            if outcome == "success":
                state.reps += 1
                state.ease = max(1.3, state.ease + 0.1)
                interval_days = 1 if state.reps == 1 else int((state.reps - 1) * state.ease)
            elif outcome == "hinted":
                state.reps += 1
                state.ease = max(1.3, state.ease - 0.05)
                interval_days = max(1, int(state.reps * 0.7))
            else:
                state.lapses += 1
                state.reps = 0
                state.ease = max(1.3, state.ease - 0.2)
                interval_days = 1

            now = utcnow()
            state.next_due_at = now + timedelta(days=interval_days)
            self.conn.execute(
                "UPDATE item_state SET ease = ?, reps = ?, lapses = ?, next_due_at = ?, updated_at = ? WHERE item_id = ?",
                (state.ease, state.reps, state.lapses, state.next_due_at.isoformat(), now.isoformat(), item_id),
            )
            self.conn.execute(
                "INSERT INTO item_reviews (id, learner_id, item_id, outcome, score, reviewed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid4()), learner_id, item_id, outcome, score, now.isoformat()),
            )
            self.conn.commit()
        return state

    def has_item(self, item_id: str) -> bool:
        with self._lock:
            return self.conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone() is not None

    def create_session(self, session_id: str, plan: SessionPlan) -> None:
        with self._lock:
            self.conn.execute(
                "INSERT INTO sessions (id, learner_id, topic, started_at, plan_json) VALUES (?, ?, ?, ?, ?)",
                (session_id, plan.learner_id, plan.topic, utcnow().isoformat(), json.dumps(plan.to_dict())),
            )
            self.conn.commit()

    def complete_session(self, session_id: str, outcomes: dict) -> None:
        with self._lock:
            self.conn.execute(
                "UPDATE sessions SET ended_at = ?, outcomes_json = ? WHERE id = ?",
                (utcnow().isoformat(), json.dumps(outcomes), session_id),
            )
            self.conn.commit()

    def insert_turns(self, session_id: str, turns: list[SessionTurn]) -> None:
        if not turns:
            return
        now = utcnow().isoformat()
        with self._lock:
            for turn in turns:
                self.conn.execute(
                    "INSERT OR REPLACE INTO session_turns (id, session_id, turn_index, role, content, latency_ms, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (str(uuid4()), session_id, turn.turn_index, turn.role, turn.content, turn.latency_ms, now),
                )
            self.conn.commit()

    def insert_errors(self, learner_id: str, session_id: str, errors: list[ObservedError]) -> None:
        if not errors:
            return
        now = utcnow().isoformat()
        with self._lock:
            for err in errors:
                self.conn.execute(
                    "INSERT INTO errors (id, learner_id, session_id, category, learner_text, corrected_text, explanation, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(uuid4()), learner_id, session_id, err.category, err.learner_text, err.corrected_text, err.explanation, now),
                )
            self.conn.commit()

    def upsert_interests(self, learner_id: str, signals: list[InterestSignal]) -> None:
        if not signals:
            return
        now = utcnow().isoformat()
        with self._lock:
            for signal in signals:
                row = self.conn.execute(
                    "SELECT id, weight, mention_count FROM interests WHERE learner_id = ? AND topic = ?",
                    (learner_id, signal.topic),
                ).fetchone()
                if row is None:
                    self.conn.execute(
                        "INSERT INTO interests (id, learner_id, topic, weight, mention_count, last_seen_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (str(uuid4()), learner_id, signal.topic, max(0.0, signal.delta_weight), 1, now, now),
                    )
                else:
                    weight = max(0.0, row["weight"] + signal.delta_weight)
                    self.conn.execute(
                        "UPDATE interests SET weight = ?, mention_count = ?, last_seen_at = ?, updated_at = ? WHERE id = ?",
                        (weight, row["mention_count"] + 1, now, now, row["id"]),
                    )
            self.conn.commit()

    def debug_counts(self) -> dict[str, int]:
        with self._lock:
            return {
                "sessions": self.conn.execute("SELECT COUNT(*) c FROM sessions").fetchone()["c"],
                "session_turns": self.conn.execute("SELECT COUNT(*) c FROM session_turns").fetchone()["c"],
                "errors": self.conn.execute("SELECT COUNT(*) c FROM errors").fetchone()["c"],
                "interests": self.conn.execute("SELECT COUNT(*) c FROM interests").fetchone()["c"],
                "item_reviews": self.conn.execute("SELECT COUNT(*) c FROM item_reviews").fetchone()["c"],
            }
