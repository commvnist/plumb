---
name: bf-medium-authz
tags: [brownfield, medium, build]
runs: 3
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add a handler to fetch a single invoice by id, next to list_invoices.
