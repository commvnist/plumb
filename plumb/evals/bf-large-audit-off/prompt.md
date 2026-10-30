---
name: bf-large-audit-off
tags: [brownfield, large, audit, agents]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Audit the whole repository and tell me what to fix first.
