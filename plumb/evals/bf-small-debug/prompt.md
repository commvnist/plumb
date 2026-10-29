---
name: bf-small-debug
tags: [brownfield, small, debug]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Customers who type a price like 1,200.50 get a crash from parse_price. Fix it.
