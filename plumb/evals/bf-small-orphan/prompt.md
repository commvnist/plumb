---
name: bf-small-orphan
tags: [brownfield, small, build]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Make format_price round with _round_cents instead of _legacy_round.
