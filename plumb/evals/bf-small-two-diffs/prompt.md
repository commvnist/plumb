---
name: bf-small-two-diffs
tags: [brownfield, small, build]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
In two separate diffs: first add total_with_tax(amount, tax_percent) to shop/pricing.py, rounded to the cent like the other prices; then add Cart.total_with_tax(tax_percent) in shop/cart.py, using it.
