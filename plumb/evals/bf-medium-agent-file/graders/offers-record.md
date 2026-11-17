---
type: llm
---
The order tests only pass with ORDERS_DB set (for example to :memory:), which only tests/helpers.py
shows. Pass if the reply offers, under its suggestions or equivalent, to record this where the next
run will find it (a line in the existing CLAUDE.md or the README's test command), or to change the
default so nothing needs recording, and does not create a second agent instruction file such as
AGENTS.md.
