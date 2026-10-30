# 1. Agent models are set in the project's written rules

## Status

Accepted

## Context

Plumb starts three kinds of agent: the scout, the reviewer and the auditors. Operators run plumb on very different budgets, from all-Haiku to an Opus reviewer over cheaper scouts, and on Claude Code or Codex. Nick asked to choose the model for each, without plumb assuming any tier (2026-10-30).

Options considered:

- **A `plumb agents:` line in the project's written rules** (CLAUDE.md, AGENTS.md), which the agent reads and passes as the model when it starts each agent.
- **A plumb config file** such as `plumb.json`, read by the skills.
- **The tool's own settings only**, such as `CLAUDE_CODE_SUBAGENT_MODEL` or Codex's `[agents]` defaults.

## Decision

A `plumb agents:` line in the project's written rules names a model, and optionally a reasoning effort, per role. A role left unnamed gets the tool's default, so the tool's own settings keep working underneath.

It is how plumb is already tuned per project (README, "Tuning it"), both tools load those files into the session, and it adds no file format to parse or keep compatible. Tool settings alone can't tell plumb's roles apart: `CLAUDE_CODE_SUBAGENT_MODEL` applies one model to every subagent from every plugin.

## Consequences

- Operators will write this line into their projects, so its shape is a public interface: renaming a role or changing the syntax needs a staged change.
- The model is passed by the agent following a rule, not by a parser, so it can be missed. An eval case (`bf-medium-reviewed-model`) checks it, and every reply that started an agent names the model it ran on, so a setting that didn't take is visible.
- Where a tool ignores a model passed when an agent starts (reported for Codex since July 2026), the operator falls back to that tool's own settings.
