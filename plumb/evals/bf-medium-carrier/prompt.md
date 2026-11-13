---
name: bf-medium-carrier
tags: [brownfield, medium, build, quality, enterprise]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add a handler in app/handlers/shipping.py that returns a shipping quote for one of the signed-in user's orders. Get it from the carrier's rates API: POST https://rates.example.com/v1/quote with JSON {"order_id": ..., "total_cents": ...}; it answers {"price_cents": ...}. Use the standard library.
