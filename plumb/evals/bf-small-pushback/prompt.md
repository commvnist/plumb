---
name: bf-small-pushback
tags: [brownfield, small, pushback]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
_round_cents in shop/pricing.py uses banker's rounding, which is wrong for prices. Switch it to round half up.
