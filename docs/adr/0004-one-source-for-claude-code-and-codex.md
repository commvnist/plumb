# 4. One source for Claude Code and Codex

## Status

Accepted

## Context

commvnist asked for plumb to support OpenAI Codex as well as Claude Code (2026-10-30). Codex reads the same `SKILL.md` format, but its plugin manifest (`.codex-plugin/plugin.json`), marketplace (`.agents/plugins/marketplace.json`) and custom agents (TOML files in `~/.codex/agents/` or `.codex/agents/`) differ, and its plugins have no documented way to ship agents. Codex couldn't be run while this was written, so its behaviour comes from OpenAI's documentation and its curated plugins repository, not a test.

Options considered:

- **One source**: Claude Code's files stay the source; a script writes Codex's manifest, marketplace entry and agent TOML from them, and CI fails when they drift.
- **A separate Codex copy** of the skills and agents, edited by hand.
- **Skills only**: ship the skills to Codex and leave the agents out.

## Decision

One source. `scripts/build_codex.py` writes the Codex files; `--check` runs in CI. The skills themselves need no conversion. Operators copy the generated agent files into a Codex agents folder, since Codex plugins can't carry them.

A hand-kept copy would let every rule drift between two places, which CONTRIBUTING's "say it once" exists to prevent. Leaving the agents out would lose the independent reviewer on Codex.

## Consequences

- Codex support is untested until someone runs it; the README says so.
- On Codex, agents can't be made read-only per agent (they inherit the session's sandbox), so the reviewer's and auditor's "change nothing" is an instruction there, not a guarantee.
- Codex reportedly ignores a model passed when starting an agent (since July 2026); per-role models there come from a `model` line added to the copied agent file or Codex's `[agents]` defaults.
- The session-start hook runs on Codex only after the user trusts it, and plugins with hooks can't be listed in Codex's public directory.
