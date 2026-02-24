# SPEC — conversational AI tutor with spaced repetition

## 1. Goals
- Users improve listening + speaking in novel situations (transfer).
- Daily sessions feel like real conversation but still execute SRS.

## 2. Non-goals (for MVP)
- Perfect speech grading
- Many languages
- Social leagues

## 3. MVP user loop (7–12 mins)
1) Warm start: topic from interest profile
2) Conversation segment (input + interaction)
3) Embedded retrieval: 6–12 due items (chunks/patterns) inserted naturally
4) Short output task: speak or write a response
5) End-of-session recap + next “due” preview

## 4. System architecture (MVP)
Client -> API -> Orchestrator -> LLM Teacher
                    |-> Learner State DB (Postgres)
                    |-> Audit Log (messages)
                    |-> Scheduler (worker/cron)
                    |-> Vector index (optional MVP)

## 5. Data model (MVP)
- users
- sessions
- messages (audit log)
- items (chunks/patterns/pron targets)
- reviews (attempt results)
- interest_signals

## 6. Agent contracts (MVP)
Teacher agent must output JSON:
- session_summary
- review_events[] (item_id, result, latency_ms, mode, hint_used)
- new_items[] (type, canonical_form, meaning, examples, tags)
- interest_signals[] (topic, weight_delta, evidence)

Backend validates JSON Schema and applies updates.

## 7. Scheduling rules (MVP)
- start with a simple SM-2-like scheduler
- failures re-teach via input + quick retry; do not just repeat quizzes
- cap due items per session; prioritize high-utility items

## 8. Acceptance tests
- A golden simulated session inserts at least N due items naturally
- All agent outputs validate schema
- Scheduler produces stable next_due timestamps and is deterministic
