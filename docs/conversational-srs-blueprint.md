# Conversational SRS Product Blueprint (Day 1-30)

## 1) Core architecture

1. **Conversation Orchestrator (Director)**
   - Inputs: learner id, time, recent context.
   - Outputs: session plan (due items, topic, activity mix, constraints).
2. **Teacher Agent (LLM)**
   - Runs conversation naturally while embedding retrieval practice.
   - Emits **structured proposed updates** only (never mutates memory directly).
3. **Learner Model Store (DB + optional vector search)**
   - Source of truth for item mastery, review history, errors, interests, and sessions.
4. **SRS Scheduler**
   - Start with SM-2-like update logic.
   - Computes `next_due_at` from success, effort, and stability signals.
5. **Transparency Layer**
   - Generates readable `.md` learner snapshots from DB state.

---

## 2) Deterministic learner-state schema

Use the SQL schema in `db/schema.sql`. Key entities:

- `learners`: profile + preferences.
- `interests`: weighted topic model with recency.
- `items`: atomic learnable units (chunk, grammar, pronunciation, confusion_pair).
- `item_reviews`: immutable review events.
- `item_state`: scheduler-facing per-item memory state.
- `sessions`: conversation sessions with plan + outcomes.
- `errors`: normalized error log for high-value remediation.
- `session_turns`: full conversational audit trail.

This split keeps scheduling deterministic while preserving full history.

---

## 3) Session planner logic (before chat)

Given learner `L` and now `T`:

1. Pull due candidates:
   - `item_state.next_due_at <= T`
   - prioritize: overdue > weak stability > strategic curriculum gaps.
2. Cap agenda:
   - 6-12 items total.
   - include 1-2 grammar/pattern targets.
3. Choose topic:
   - maximize `interest_weight * recency_boost`
   - constrain by curriculum backbone (avoid topic-only drift).
4. Build activity mix (example):
   - 50% flow conversation,
   - 25% retrieval checks,
   - 15% recast/correction,
   - 10% reflection + confidence check.
5. Emit session plan JSON for teacher prompt grounding.

---

## 4) In-session teacher behavior contract

Teacher must:

- Make due items necessary in context (not list-drilling).
- Run short retrieval probes:
  - cloze,
  - “say it another way,”
  - “how would you reply?”.
- Recast and briefly explain errors.
- Recycle targets later in new contexts (interleaving).
- Track evidence for each target (success/fail, hints, latency, confidence).

Teacher output must include a machine-readable `proposed_updates` block.

---

## 5) Post-session update pipeline

1. Validate `proposed_updates` against schema + business rules.
2. Insert immutable events:
   - `item_reviews`, `errors`, `sessions`, `session_turns`.
3. Recompute `item_state`:
   - adjust ease/stability,
   - set `next_due_at`.
4. Extract new candidate items from high-value utterances/corrections.
5. Update `interests` weights from engagement signals.
6. Generate optional learner `.md` snapshot.

---

## 6) Day 1-30 execution plan

### Days 1-3: Foundations
- Finalize schema and migrations.
- Implement write/read APIs for learners, items, reviews, sessions.
- Add deterministic scheduler function (SM-2 baseline).

### Days 4-7: First guided sessions
- Implement planner service producing session plan JSON.
- Implement teacher prompt assembly from retrieved state.
- Save full turn-level audit logs.

### Days 8-12: Reliable memory updates
- Introduce strict JSON schema for `proposed_updates`.
- Add server-side validator and reject invalid updates.
- Add idempotent post-session processing pipeline.

### Days 13-18: Adaptivity + interest model
- Add interest scoring updates from turns.
- Add curriculum backbone constraints to planner.
- Introduce confusion-pair targeting in agenda selection.

### Days 19-24: UX quality of learning loop
- Add in-session interleaving policy.
- Add confidence + latency capture in retrieval probes.
- Add learner snapshot generation endpoint (`.md`).

### Days 25-30: Evaluation + hardening
- Metrics: recall lift, due-item completion, correction uptake, retention by topic.
- Build offline replay tests from session logs.
- Tune scheduler thresholds and item caps.

---

## 7) Guardrails against common failure modes

- **Token overflow:** retrieve only agenda, top errors, and topic profile.
- **Hallucinated progress:** model proposes; backend verifies + writes.
- **Test-like feel:** maintain high flow-talk proportion.
- **Coverage gaps:** enforce backbone syllabus constraints.
