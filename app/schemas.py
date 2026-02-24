from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class CreateItemRequest:
    learner_id: str
    item_type: Literal["chunk", "grammar", "pronunciation", "confusion_pair"]
    prompt_form: str
    target_form: str


@dataclass
class PlanRequest:
    learner_id: str


@dataclass
class ReviewedItem:
    item_id: str
    outcome: Literal["success", "fail", "hinted"]
    latency_ms: int | None = None
    confidence: float | None = None
    evidence: str | None = None


@dataclass
class ObservedError:
    category: str
    learner_text: str
    corrected_text: str
    explanation: str | None = None


@dataclass
class InterestSignal:
    topic: str
    delta_weight: float
    reason: str | None = None


@dataclass
class SessionTurn:
    turn_index: int
    role: Literal["user", "assistant", "system"]
    content: str
    latency_ms: int | None = None


@dataclass
class ProposedUpdates:
    reviewed_items: list[ReviewedItem] = field(default_factory=list)
    observed_errors: list[ObservedError] = field(default_factory=list)
    interest_signals: list[InterestSignal] = field(default_factory=list)
    session_turns: list[SessionTurn] = field(default_factory=list)


@dataclass
class FinalizeRequest:
    proposed_updates: ProposedUpdates

    @staticmethod
    def from_payload(payload: dict) -> "FinalizeRequest":
        updates = payload.get("proposed_updates", {})
        return FinalizeRequest(
            proposed_updates=ProposedUpdates(
                reviewed_items=[ReviewedItem(**row) for row in updates.get("reviewed_items", [])],
                observed_errors=[ObservedError(**row) for row in updates.get("observed_errors", [])],
                interest_signals=[InterestSignal(**row) for row in updates.get("interest_signals", [])],
                session_turns=[SessionTurn(**row) for row in updates.get("session_turns", [])],
            )
        )


@dataclass
class SessionPlan:
    learner_id: str
    generated_at: datetime
    due_items: list[dict]
    topic: str
    activity_mix: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "learner_id": self.learner_id,
            "generated_at": self.generated_at.isoformat(),
            "due_items": self.due_items,
            "topic": self.topic,
            "activity_mix": self.activity_mix,
        }
