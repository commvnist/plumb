---
name: bf-small-risk-named
tags: [brownfield, small, build, pushback]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Make parse_price in shop/pricing.py return 0 when the text isn't a valid number, instead of raising.
