# 3. Every agent use works without agents

## Status

Accepted

## Context

Plumb's scout, reviewer and auditors save context and give a review fresh eyes. Some operators can't or won't run subagents: their budget has no room for them, their tool or plan doesn't offer them, or they turned them off (Claude Code: deny the `Agent` tool; Codex: `agents.enabled = false`). Nick asked plumb to support that case (2026-10-30).

Options considered:

- **Each agent use says what to do without one**, and the report names what was lost.
- **Require agents**, and tell operators without them that plumb won't fully work.
- **Drop the agents**, doing everything in the session.

## Decision

Agents are a saving, never a requirement. With agents off in the project's written rules (`plumb agents: off`), or when the tool can't start one, the session does the role's work. The one thing lost is the independence of a review of the session's own work, so the session self-reviews, says under Unverified that no independent review ran, and offers one in a fresh session given only the change and its goal. Audits take one area at a time and keep only its findings before the next.

Requiring agents would shut out the smallest budgets plumb is meant to fit. Dropping them would make every operator pay for whole-repository reads in the main context.

## Consequences

- No rule in the charter may depend on an agent existing; a new agent needs a stated fallback.
- With agents off, a whole-repository audit runs in one context and costs more of it; very large repositories may need the operator to name areas.
- Eval cases `bf-large-audit-off` and `bf-medium-reviewed-off` check both fallbacks.
