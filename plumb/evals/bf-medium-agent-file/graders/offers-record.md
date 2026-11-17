---
type: llm
---
The test suite only runs with ORDERS_TEST=1 set, which neither CLAUDE.md nor the README says.
Pass only if the reply offers (or, if it already did it, reports) a line in the repository's
existing agent instruction file, CLAUDE.md, or in the README's test command, recording that the
tests need ORDERS_TEST=1, with what it saves the next run; and it does not create a second agent
instruction file such as AGENTS.md.
