# Product Alignment Playbook

This repository was initialized without implementation artifacts, so the fastest way to narrow the gap between the **original vision** and what gets built is to make alignment explicit and enforce it in weekly execution.

## 1) Vision Lock (One Source of Truth)

Create a one-page vision doc and keep it current. At minimum include:

- **Problem statement**: what user pain exists now.
- **Target user**: who this is for (and who it is not for).
- **North-star outcome**: measurable behavior change or business metric.
- **Non-goals**: what will intentionally not be built in this phase.
- **Design principles**: 3–5 principles used to make tradeoffs.

If this section is missing, teams naturally drift toward implementation convenience instead of product intent.

## 2) Build a Gap Map

Map every currently shipped/planned item to the vision.

Use this format:

| Item | Supports Vision? | Evidence | Action |
|---|---|---|---|
| Feature / workflow | High / Medium / Low | User data, qualitative feedback, metric impact | Keep, revise, or remove |

Decision rule:

- **High + Evidence** → keep and improve.
- **Medium + mixed evidence** → tighten scope and test.
- **Low alignment** → deprecate or stop investing.

## 3) Convert Vision Into Measurable Milestones

Break the vision into 6–8 week milestones with explicit success criteria.

Template per milestone:

- **Hypothesis**: “If we build X for Y user, metric Z will improve by N%.”
- **Leading metric**: early signal (activation, completion, retention proxy).
- **Guardrail metric**: ensure no quality regressions.
- **Exit criteria**: objective condition to move forward, pivot, or stop.

## 4) Prioritize Using Alignment-First Scoring

Before committing to work, score each candidate:

- **Vision Alignment (0–5)**
- **User Value (0–5)**
- **Confidence (0–5)**
- **Effort (0–5, reverse)**

Recommended score:

`Priority = (2 × Alignment + User Value + Confidence) - Effort`

Anything with weak alignment should be challenged even if easy.

## 5) Tighten the Product Loop

Adopt a fixed weekly cadence:

1. **Monday**: choose top 1–2 vision-critical bets.
2. **Midweek**: review with design/engineering on principles and non-goals.
3. **Friday**: compare outcomes vs hypothesis and capture learnings.
4. **Retrospective**: identify drift causes and prevention actions.

## 6) Add Decision Hygiene

Every meaningful feature decision should include:

- the user problem
- the expected metric movement
- alternatives considered
- why this aligns with vision
- what would invalidate the decision

Store these as short decision records to reduce repeated debates and memory loss.

## 7) 30-Day Recovery Plan

### Week 1 — Diagnose

- Finalize one-page vision.
- Complete gap map for all active items.
- Flag low-alignment work for pause.

### Week 2 — Re-scope

- Rebuild roadmap around top 2–3 aligned opportunities.
- Define measurable hypotheses and success criteria.

### Week 3 — Execute

- Ship smallest testable slice for top opportunity.
- Track leading and guardrail metrics daily.

### Week 4 — Decide

- Keep/pivot/kill based on evidence.
- Publish updated roadmap and rationale.

## Practical Artifacts to Add Next

- `docs/vision.md` — single-source product vision
- `docs/gap-map.md` — alignment audit of current scope
- `docs/roadmap.md` — milestone roadmap with hypotheses
- `docs/decisions/` — lightweight decision records

---

If helpful, the next step can be to generate these four docs with starter templates so the team can begin alignment immediately.
