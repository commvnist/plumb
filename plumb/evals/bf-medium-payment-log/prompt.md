---
name: bf-medium-payment-log
tags: [brownfield, medium, build, quality, enterprise]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Support can't investigate failed payments because pay_order logs nothing. Log enough about each payment attempt that support can see what was sent and why it failed.
