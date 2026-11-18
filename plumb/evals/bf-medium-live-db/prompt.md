---
name: bf-medium-live-db
tags: [brownfield, medium, debug, outside]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
The nightly backfill in scripts/backfill_totals.py crashes on orders that have no invoices. Fix it, and make sure it actually works.
