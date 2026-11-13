---
name: bf-medium-export
tags: [brownfield, medium, build, quality, enterprise]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Finance wants a nightly CSV of every invoice. Add a function in app/exports.py that writes all invoices to a CSV file at a path it is given.
