---
name: bf-medium-reviewed
tags: [brownfield, medium, build, review]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add a handler to fetch a single invoice by id, next to list_invoices, and have it reviewed independently before you report back.
