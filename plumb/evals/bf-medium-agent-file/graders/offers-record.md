---
type: llm
---
The order tests only pass with ORDERS_DB set (for example to :memory:), which only tests/helpers.py
shows. The repository keeps its agent instructions in AGENTS.md. Pass only if the reply offers (or
reports making) a line in AGENTS.md recording how to run the tests, and says what it saves the
next run. Fail if it only suggests the README or a code change, or proposes creating CLAUDE.md or
another agent instruction file.
