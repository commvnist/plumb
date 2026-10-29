---
name: gf-medium-api
tags: [greenfield, medium, build]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Build a small JSON HTTP API in Python for a todo list (create, list, complete, delete) that keeps its data across restarts.
