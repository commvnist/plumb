---
name: bf-medium-plan
tags: [brownfield, medium, plan]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Rename the order status field to state everywhere, including the database column.
