---
name: bf-medium-event-rename
tags: [brownfield, medium, build, plan]
runs: 1
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
---
Rename the order_id field of shipment.dispatched messages to order_ref, in app/shipping.py which publishes them and in the consumer that handles them.
