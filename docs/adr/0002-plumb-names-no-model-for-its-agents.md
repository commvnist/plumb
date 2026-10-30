# 2. Plumb names no model for its agents

## Status

Accepted

## Context

Up to 0.4.0's review, plumb's agent definitions fixed their model: the scout and auditor to Sonnet, the reviewer to `inherit`. On Claude Code, a model in an agent's definition, `inherit` included, outranks `CLAUDE_CODE_SUBAGENT_MODEL`, so a fixed model locked operators out of their own setting. A named tier also fails accounts that lack it or pay differently for it, and means nothing on Codex.

Options considered:

- **Name no model**: leave the field out, so the tool's default applies (the model passed when starting the agent, then the operator's subagent setting, then the session's model).
- **Keep Sonnet for the scout and auditor**, as 0.4.0's review proposed, to save cost on Opus sessions.
- **`inherit` everywhere**: always the session's model.

## Decision

Name no model in any agent definition. commvnist chose this on 2026-10-30 so plumb fits any budget. The Sonnet pins bought nothing measured (0.4.0's evals already ran on Sonnet), and `inherit` blocks the operator's override just as a named model does. The change landed in PR #6 (commit 31cfbc3); this record follows it.

## Consequences

- An operator who sets nothing runs every agent on their session's model. On an expensive session model, scouts and auditors cost more than under 0.4.0's review draft; the README's "Choosing models" says where a cheaper model is enough.
- A future change that wants a default tier for a role must supersede this record.
