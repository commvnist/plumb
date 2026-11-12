# 6. Copilot CLI reads the Claude Code plugin

## Status

Accepted

## Context

commvnist asked for plumb to support GitHub Copilot (2026-11-12), in keeping with fitting a wide range of tools and budgets. Copilot CLI 1.0.109 was run against plumb with a stand-in model on a local endpoint, which showed what it loads without needing a Copilot account. It reads `.claude-plugin/marketplace.json` and `plugin.json`, the `SKILL.md` skills, the Claude Code agent files (keeping their tool limits and accepting a model when one is started) and `hooks/hooks.json`, and it sets `CLAUDE_PLUGIN_ROOT`. The one difference: it takes a hook's context only from JSON with a top-level `additionalContext`, so it ignored plumb's plain-text session reminder and the commit check's `hookSpecificOutput`.

Options considered:

- **Use the Claude Code plugin as is**, with each hook writing the shape the running tool reads, told apart by `COPILOT_PLUGIN_ROOT`, which only Copilot sets.
- **Generate Copilot files** (a manifest, `.agent.md` agents and a hooks file in Copilot's own format) from the Claude Code sources, as `scripts/build_codex.py` does for Codex.
- **Skills only**, leaving out the agents and hooks.

## Decision

Use the plugin as is. Nothing Copilot reads needs a second copy or a generator, so "one source" (ADR 4) holds with no build step; only the two hooks change, and only in how they print. Generated files would add a manifest Copilot prefers over the one it already reads, for no part that doesn't work today. Skills only would lose the independent reviewer and the commit check.

## Consequences

- Each hook prints one of two shapes, chosen by an environment variable. If Copilot stops setting `COPILOT_PLUGIN_ROOT`, or another tool starts setting it, the hooks print the wrong shape and their text silently stops reaching the agent; `scripts/test_session_start.py` and `scripts/test_check_commit.py` cover both shapes, not the variable itself.
- Copilot's own models haven't been used for real work with plumb, so how well they follow the skills is unknown; the README says so.
- Copilot's cloud agent loads no plugins, and VS Code's plugin support hasn't been tried; both are outside this decision.
