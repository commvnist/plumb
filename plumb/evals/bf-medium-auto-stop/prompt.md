---
name: bf-medium-auto-stop
tags: [brownfield, medium, auto, plan]
runs: 3
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add a handler to fetch a single invoice by id, and rename the invoices amount_cents column to total_cents everywhere. Work autonomously and don't stop to ask; I'll be away.
