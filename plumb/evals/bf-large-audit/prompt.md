---
name: bf-large-audit
tags: [brownfield, large, audit]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Audit the tests in tests/billing: which are useless, and what's missing?
