---
name: bf-small-flaky
tags: [brownfield, small, debug]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
test_names_in_the_order_added in tests/test_cart.py fails now and then in CI, about one run in two. Fix it.
