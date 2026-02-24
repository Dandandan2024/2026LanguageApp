from __future__ import annotations

import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from uuid import uuid4

from app.schemas import CreateItemRequest, FinalizeRequest, PlanRequest, SessionPlan
from app.store import SQLiteStore, Store


class BackendService:
    def __init__(self, store: Store | None = None) -> None:
        self.store = store or SQLiteStore()
        self.session_plans: dict[str, SessionPlan] = {}

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def create_item(self, body: CreateItemRequest) -> dict:
        item = self.store.create_item(
            learner_id=body.learner_id,
            item_type=body.item_type,
            prompt_form=body.prompt_form,
            target_form=body.target_form,
        )
        return {"item_id": item.id}

    def plan_session(self, body: PlanRequest) -> dict:
        now = datetime.now(timezone.utc)
        due_rows = self.store.due_items(body.learner_id, now)
        plan = SessionPlan(
            learner_id=body.learner_id,
            generated_at=now,
            due_items=[
                {
                    "item_id": row["item"].id,
                    "item_type": row["item"].item_type,
                    "prompt_form": row["item"].prompt_form,
                    "target_form": row["item"].target_form,
                    "next_due_at": row["state"].next_due_at.isoformat(),
                }
                for row in due_rows
            ],
            topic="general conversation",
            activity_mix={"flow_talk": 50, "retrieval": 25, "recast": 15, "reflection": 10},
        )
        session_id = str(uuid4())
        self.session_plans[session_id] = plan
        self.store.create_session(session_id, plan)
        return {"session_id": session_id, "plan": plan.to_dict()}

    def finalize_session(self, session_id: str, body: FinalizeRequest) -> dict:
        if session_id not in self.session_plans:
            raise ValueError("Unknown session")

        plan = self.session_plans[session_id]
        applied = []
        for review in body.proposed_updates.reviewed_items:
            if not self.store.has_item(review.item_id):
                raise ValueError(f"Unknown item_id: {review.item_id}")
            state = self.store.apply_review(plan.learner_id, review.item_id, review.outcome, review.confidence)
            applied.append(
                {
                    "item_id": review.item_id,
                    "next_due_at": state.next_due_at.isoformat(),
                    "reps": state.reps,
                    "lapses": state.lapses,
                }
            )

        self.store.insert_turns(session_id, body.proposed_updates.session_turns)
        self.store.insert_errors(plan.learner_id, session_id, body.proposed_updates.observed_errors)
        self.store.upsert_interests(plan.learner_id, body.proposed_updates.interest_signals)
        self.store.complete_session(
            session_id,
            {
                "applied_review_count": len(applied),
                "error_count": len(body.proposed_updates.observed_errors),
                "interest_signal_count": len(body.proposed_updates.interest_signals),
                "turn_count": len(body.proposed_updates.session_turns),
            },
        )

        return {"session_id": session_id, "applied_reviews": applied}


def make_handler(service: BackendService):
    class ApiHandler(BaseHTTPRequestHandler):
        def _write(self, status: HTTPStatus, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length) if length > 0 else b"{}")

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._write(HTTPStatus.OK, service.health())
                return
            self._write(HTTPStatus.NOT_FOUND, {"detail": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            try:
                data = self._read_json()
                if self.path == "/items":
                    self._write(HTTPStatus.OK, service.create_item(CreateItemRequest(**data)))
                    return

                if self.path == "/sessions/plan":
                    self._write(HTTPStatus.OK, service.plan_session(PlanRequest(**data)))
                    return

                if self.path.startswith("/sessions/") and self.path.endswith("/finalize"):
                    session_id = self.path.split("/")[2]
                    self._write(HTTPStatus.OK, service.finalize_session(session_id, FinalizeRequest.from_payload(data)))
                    return

                self._write(HTTPStatus.NOT_FOUND, {"detail": "Not found"})
            except (TypeError, ValueError, KeyError) as exc:
                self._write(HTTPStatus.BAD_REQUEST, {"detail": str(exc)})

    return ApiHandler


def run_server(host: str = "127.0.0.1", port: int = 8000, db_path: str = "data/languageapp.db") -> None:
    service = BackendService(store=SQLiteStore(db_path=db_path))
    server = ThreadingHTTPServer((host, port), make_handler(service))
    server.serve_forever()


if __name__ == "__main__":
    run_server()
