---
name: bf-medium-consumer
tags: [brownfield, medium, build]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add a consumer that marks an order paid when a payment.succeeded event arrives.
