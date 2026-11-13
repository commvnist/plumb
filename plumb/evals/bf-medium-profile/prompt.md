---
name: bf-medium-profile
tags: [brownfield, medium, build, quality]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Add a handler in app/handlers/users.py that returns the signed-in user's profile.
