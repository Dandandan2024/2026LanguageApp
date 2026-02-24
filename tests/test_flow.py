import json
import tempfile
import threading
import unittest
from urllib import error, request

from app.main import BackendService, make_handler
from app.schemas import CreateItemRequest, FinalizeRequest, PlanRequest, ProposedUpdates, ReviewedItem
from app.store import SQLiteStore
from http.server import ThreadingHTTPServer


class FlowTests(unittest.TestCase):
    def test_plan_and_finalize_flow_persists_artifacts(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            store = SQLiteStore(db_path=f.name)
            service = BackendService(store=store)
            learner_id = "learner-1"

            created = service.create_item(
                CreateItemRequest(
                    learner_id=learner_id,
                    item_type="chunk",
                    prompt_form="I am up for",
                    target_form="I'm up for",
                )
            )
            item_id = created["item_id"]

            planned = service.plan_session(PlanRequest(learner_id=learner_id))
            session_id = planned["session_id"]

            finalized = service.finalize_session(
                session_id,
                FinalizeRequest.from_payload(
                    {
                        "proposed_updates": {
                            "reviewed_items": [
                                {"item_id": item_id, "outcome": "success", "confidence": 0.8}
                            ],
                            "observed_errors": [
                                {
                                    "category": "grammar",
                                    "learner_text": "yesterday I go",
                                    "corrected_text": "yesterday I went",
                                    "explanation": "past tense irregular",
                                }
                            ],
                            "interest_signals": [
                                {"topic": "travel", "delta_weight": 0.4, "reason": "high engagement"}
                            ],
                            "session_turns": [
                                {"turn_index": 1, "role": "user", "content": "hi"},
                                {"turn_index": 2, "role": "assistant", "content": "hello"},
                            ],
                        }
                    }
                ),
            )
            self.assertEqual(1, finalized["applied_reviews"][0]["reps"])

            counts = store.debug_counts()
            self.assertEqual(1, counts["sessions"])
            self.assertEqual(2, counts["session_turns"])
            self.assertEqual(1, counts["errors"])
            self.assertEqual(1, counts["interests"])
            self.assertEqual(1, counts["item_reviews"])

    def test_http_endpoints_and_unknown_session(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            service = BackendService(store=SQLiteStore(db_path=f.name))
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(service))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            host, port = server.server_address
            base = f"http://{host}:{port}"

            try:
                self.assertEqual(200, request.urlopen(f"{base}/health", timeout=2).status)

                create_req = request.Request(
                    f"{base}/items",
                    data=json.dumps(
                        {
                            "learner_id": "learner-http",
                            "item_type": "grammar",
                            "prompt_form": "yesterday I go",
                            "target_form": "yesterday I went",
                        }
                    ).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                item_id = json.loads(request.urlopen(create_req, timeout=2).read())["item_id"]

                plan_req = request.Request(
                    f"{base}/sessions/plan",
                    data=json.dumps({"learner_id": "learner-http"}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                session_id = json.loads(request.urlopen(plan_req, timeout=2).read())["session_id"]

                finalize_req = request.Request(
                    f"{base}/sessions/{session_id}/finalize",
                    data=json.dumps(
                        {
                            "proposed_updates": {
                                "reviewed_items": [{"item_id": item_id, "outcome": "hinted", "confidence": 0.6}],
                                "session_turns": [{"turn_index": 1, "role": "user", "content": "hello"}],
                            }
                        }
                    ).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                finalize_payload = json.loads(request.urlopen(finalize_req, timeout=2).read())
                self.assertEqual(1, finalize_payload["applied_reviews"][0]["reps"])

                bad_finalize = request.Request(
                    f"{base}/sessions/does-not-exist/finalize",
                    data=json.dumps({"proposed_updates": {"reviewed_items": []}}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(error.HTTPError) as ctx:
                    request.urlopen(bad_finalize, timeout=2)
                self.assertEqual(400, ctx.exception.code)
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
