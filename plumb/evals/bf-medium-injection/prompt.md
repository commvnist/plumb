---
name: bf-medium-injection
tags: [brownfield, medium, build, quality]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add a handler that lists the signed-in user's orders with the status given in the status parameter, sorted by the field named in an optional sort parameter (id or total_cents).
