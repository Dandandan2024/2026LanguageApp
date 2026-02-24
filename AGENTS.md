# AGENTS.md — language learning app (AI tutor + SRS)

## Product intent (non-negotiable)
We are building a conversation-first language learning app that:
- maximizes long-term retention + real-world transfer (not lesson completion)
- uses a deterministic learner model + spaced repetition scheduler
- adapts topics to user interests without losing core syllabus coverage
- never lets the LLM directly mutate state; it proposes structured updates only

## Definition of done (for every task)
- tests pass (unit + contract/schema)
- any new API has a typed interface + minimal docs
- changes match SPEC.md acceptance criteria
- no “magic memory”: learner state updates must go through validated schemas

## Commands
- Install: <fill in>
- Dev: <fill in>
- Test: <fill in>
- Lint/format: <fill in>
- DB migrate/reset: <fill in>

## Repo layout (expected)
- docs/SPEC.md (source of truth)
- apps/* (client apps)
- services/api (HTTP API)
- services/worker (scheduler + background jobs)
- packages/shared (types + schemas)
- evals/ (golden conversation tests)

## Coding conventions
- prefer explicit types + pure functions for scheduler logic
- all agent outputs must validate against JSON Schema in packages/shared/schemas
- store all “full chat logs” as audit log; store “learner state” separately (DB)
