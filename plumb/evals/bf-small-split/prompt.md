---
name: bf-small-split
tags: [brownfield, small, build, quality]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add split_bill(amount, people) to shop/pricing.py: it returns the list of amounts each person pays when a bill is split evenly.
