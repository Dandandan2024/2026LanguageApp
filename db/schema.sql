-- Minimal deterministic learner model schema (PostgreSQL)

CREATE TABLE IF NOT EXISTS learners (
  id UUID PRIMARY KEY,
  display_name TEXT NOT NULL,
  target_language TEXT NOT NULL,
  native_language TEXT NOT NULL,
  cefr_goal TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS interests (
  id UUID PRIMARY KEY,
  learner_id UUID NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  weight NUMERIC(6,3) NOT NULL DEFAULT 0.500,
  mention_count INT NOT NULL DEFAULT 0,
  last_seen_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (learner_id, topic)
);

CREATE TABLE IF NOT EXISTS items (
  id UUID PRIMARY KEY,
  learner_id UUID NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
  item_type TEXT NOT NULL CHECK (item_type IN ('chunk', 'grammar', 'pronunciation', 'confusion_pair')),
  prompt_form TEXT NOT NULL,
  target_form TEXT NOT NULL,
  difficulty NUMERIC(4,2) NOT NULL DEFAULT 2.50,
  tags JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_from_session_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS item_state (
  item_id UUID PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  learner_id UUID NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
  ease NUMERIC(4,2) NOT NULL DEFAULT 2.50,
  stability NUMERIC(8,3) NOT NULL DEFAULT 1.000,
  reps INT NOT NULL DEFAULT 0,
  lapses INT NOT NULL DEFAULT 0,
  last_reviewed_at TIMESTAMPTZ,
  next_due_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
  id UUID PRIMARY KEY,
  learner_id UUID NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  topic TEXT,
  plan_json JSONB NOT NULL,
  outcomes_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS session_turns (
  id UUID PRIMARY KEY,
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  turn_index INT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  latency_ms INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (session_id, turn_index)
);

CREATE TABLE IF NOT EXISTS item_reviews (
  id UUID PRIMARY KEY,
  learner_id UUID NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
  item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
  reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  outcome TEXT NOT NULL CHECK (outcome IN ('success', 'fail', 'hinted')),
  latency_ms INT,
  confidence NUMERIC(3,2),
  score NUMERIC(4,2) NOT NULL,
  evidence TEXT
);

CREATE TABLE IF NOT EXISTS errors (
  id UUID PRIMARY KEY,
  learner_id UUID NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
  session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
  category TEXT NOT NULL,
  learner_text TEXT NOT NULL,
  corrected_text TEXT NOT NULL,
  explanation TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_item_state_due ON item_state (learner_id, next_due_at);
CREATE INDEX IF NOT EXISTS idx_reviews_item_time ON item_reviews (item_id, reviewed_at DESC);
CREATE INDEX IF NOT EXISTS idx_interests_weight ON interests (learner_id, weight DESC);
