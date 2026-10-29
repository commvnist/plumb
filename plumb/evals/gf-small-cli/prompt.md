---
name: gf-small-cli
tags: [greenfield, small, build]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Write a small Python script, csv2json.py, that reads CSV on stdin and writes a JSON array of objects to stdout.
