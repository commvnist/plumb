---
name: bf-small-route-e2e
tags: [brownfield, small, routing]
runs: 3
max_turns: 4
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Build a split_bill(amount, people) helper end to end, tests included.
