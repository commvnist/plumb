---
name: bf-large-reuse
tags: [brownfield, large, build]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add rate limiting to the public billing API: 20 requests per minute per API key.
