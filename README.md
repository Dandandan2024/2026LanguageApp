# 2026LanguageApp

Deterministic conversational-SRS backend with durable local persistence and HTTP endpoints.

## Implemented now

- SQLite-backed learner store with item state, review history, sessions, turns, errors, and interests (`app/store.py`)
- Service layer for item creation, due-item planning, and finalize updates (`app/main.py`)
- Finalize pipeline stores:
  - review outcomes
  - observed errors
  - interest signals
  - turn-level session history
- HTTP API using stdlib server:
  - `GET /health`
  - `POST /items`
  - `POST /sessions/plan`
  - `POST /sessions/{session_id}/finalize`
- End-to-end tests for direct service flow and HTTP flow (`tests/test_flow.py`)

## Run tests

```bash
python -m unittest -v
```

## Run server

```bash
python -m app.main
```

The service persists data at `data/languageapp.db` by default.

## Next step

Replace the SQLite layer with PostgreSQL while keeping the same service contract and finalize update semantics.
