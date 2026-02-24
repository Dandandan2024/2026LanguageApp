# TASKS.md (Codex-ready backlog)
# Task queue (keep tasks ~1 hour)

## 0. Repo scaffolding
- [ ] Create monorepo layout + basic CI (lint/test)
- [ ] Add docs/SPEC.md and AGENTS.md, ensure tests run

## 1. Core data + contracts
- [ ] Postgres schema + migrations for users/sessions/messages/items/reviews/interests
- [ ] JSON Schemas for agent output + validator utility
- [ ] API endpoints: create_session, post_message, end_session

## 2. Scheduler
- [ ] Implement SM-2-like scheduling in services/worker
- [ ] Unit tests for scheduling edge cases (failures, lapses, caps)

## 3. Orchestration
- [ ] Session planner: selects due items + topic + prompt pack
- [ ] Teacher agent prompt + structured JSON output parsing

## 4. MVP client
- [ ] Simple chat UI + session start/end
- [ ] Display “due items used today” + recap

## 5. Evals
- [ ] Golden conversations (fixtures) + assertion checks
