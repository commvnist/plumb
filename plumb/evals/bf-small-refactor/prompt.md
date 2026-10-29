---
name: bf-small-refactor
tags: [brownfield, small, refactor]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Inline the _round_cents helper in shop/pricing.py; it is only a one-liner.
