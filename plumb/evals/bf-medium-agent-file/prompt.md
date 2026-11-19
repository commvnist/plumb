---
name: bf-medium-agent-file
tags: [brownfield, medium, debug, memory]
runs: 3
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
On a fresh checkout the order tests fail with a SQLite error. Find out how the suite is meant to be run, and run it. Change no code.
