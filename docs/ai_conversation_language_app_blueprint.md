# AI Conversation Language App Blueprint

## Product Thesis
Build an AI-native language learning app that optimizes **fluency transfer**, not lesson completion. The product should maximize:

- Comprehensible input
- Spaced retrieval and delayed retention
- Meaningful output (speaking/writing)
- Long-term motivation via autonomy, competence, and relatedness

## Core Principles (Research-Aligned)
1. **Input first, but not input only**: users should consume graded, understandable content daily.
2. **Retrieval over re-reading**: memory strengthens when learners must recall.
3. **Spacing and interleaving**: review at expanding intervals, in mixed contexts.
4. **Chunk-based instruction**: prioritize high-frequency lexical chunks and communicative intents.
5. **Conversation as the interface**: every session should feel like a meaningful dialogue.

## System Architecture

### 1) Conversation Orchestrator (Deterministic)
Backend service that plans each session before the LLM responds.

Responsibilities:
- Select due items from SRS scheduler (6–12 chunks + 1–2 grammar/pronunciation targets)
- Select topic from interest graph
- Construct session plan (input -> retrieval -> output -> recap)
- Enforce policy constraints (max corrections, challenge level, objective)

### 2) Teacher Agent (LLM)
Executes the orchestrator plan.

Responsibilities:
- Conduct natural conversation in target language
- Give contextual recasts and minimal corrections
- Ask short retrieval checks without breaking flow
- Generate structured post-session update proposals

### 3) Learner Model Store (Source of Truth)
Persisted state outside the model.

Recommended entities:
- `learners`
- `items` (chunk/grammar/pronunciation)
- `reviews` (outcome, latency, hints)
- `sessions`
- `errors` (confusion pairs, persistent mistakes)
- `interests` (weighted topics)
- `skills` (listening/speaking/reading estimates)

### 4) SRS Scheduler
Starts with SM-2 style scheduling, later replaceable.

Inputs:
- recall success/failure
- response time
- hint usage
- prior stability/difficulty

Outputs:
- next due timestamp
- updated stability and difficulty

### 5) Content Layer
- Graded dialogues and micro-stories
- Native audio in multiple accents/speeds
- Roleplay templates by intent (ordering, apologizing, negotiating, etc.)
- Pronunciation drills and shadowing clips

## Data Model (Minimal)

```sql
create table learners (
  id uuid primary key,
  native_language text not null,
  target_language text not null,
  cefr_target text,
  created_at timestamptz default now()
);

create table items (
  id uuid primary key,
  learner_id uuid references learners(id),
  item_type text check (item_type in ('chunk','grammar','pronunciation')),
  prompt text not null,
  canonical_answer text,
  utility_score numeric default 0,
  created_at timestamptz default now()
);

create table reviews (
  id uuid primary key,
  learner_id uuid references learners(id),
  item_id uuid references items(id),
  session_id uuid,
  outcome text check (outcome in ('fail','hard','good','easy')),
  latency_ms int,
  hint_used boolean default false,
  reviewed_at timestamptz default now(),
  next_due_at timestamptz
);

create table interests (
  learner_id uuid references learners(id),
  topic text,
  weight numeric default 0,
  updated_at timestamptz default now(),
  primary key (learner_id, topic)
);
```

## Session Protocol (7–12 Minutes)
1. **Input (2–4 min)**: graded story or dialogue on a preferred topic.
2. **Meaning check (1 min)**: quick comprehension checks.
3. **Retrieval (2–3 min)**: due chunk recalls and paraphrases.
4. **Output (1–3 min)**: short free response or roleplay turn.
5. **Review queue (1–2 min)**: targeted due items.

## Stealth SRS in Conversation
The user experiences this as smooth conversation while the system enforces retrieval and spacing.

- Pre-session: select due items + topic + objectives
- In-session: embed recall prompts in dialogue naturally
- Post-session: score outcomes and schedule next reviews
- Add newly emerged chunks if high utility

## Prompt Contract (Important)
The LLM should never directly mutate learner state.

Use a strict contract:
- Input: `session_plan`, `due_items`, `recent_errors`, `topic_profile`
- Output:
  - `assistant_reply` (natural language)
  - `proposed_updates` (JSON)

Backend validates and writes updates deterministically.

## Interest-Driven Curriculum Without Gaps
Use intersection strategy:

`next_content = learning_needs ∩ user_interests ∩ CEFR_backbone`

This preserves personalization while ensuring full coverage of high-frequency language.

## Metrics That Prevent False Progress

### Engagement
- D1/D7/D30 retention
- weekly active learning minutes
- session completion rate

### Learning
- delayed recall at 1/7/30 days
- listening comprehension on novel audio
- speaking task success (functional rubric)
- transfer performance on unseen scenarios

## MVP Roadmap

### Phase 1 (4–6 weeks)
- One language pair (e.g., EN -> ES)
- 150+ graded story/dialogue units
- SRS for chunks and grammar targets
- AI chat with orchestrator and correction strategy
- Learner dashboard: progress by skill + due workload

### Phase 2
- Voice mode + shadowing
- Interest graph and dynamic topic packs
- A/B tests using delayed-retention outcomes

### Phase 3
- Social features (duets, cooperative missions)
- Advanced scheduling model (stability-based)
- Multi-accent listening and role-specific tracks

## Why the `.md memory` idea is still useful
Use markdown as a **transparent learner report**, not as source of truth.

Generate snapshots like:
- goals and motivations
- active topic profile
- due item summary
- persistent errors
- last 7 session highlights

Store authoritative state in database; export `.md` for user trust and debugging.
