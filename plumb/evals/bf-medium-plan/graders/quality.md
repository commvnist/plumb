---
type: llm
---
Pass only if all hold:
- The agent produced a plan and did not change code yet, waiting for a go-ahead.
- Because the column is persisted data, the plan stages it (add the new column, migrate or dual-write, then remove the old), with migrations in app/migrations/ as the project's rules require.
- It lists the expensive decisions with options, a choice and a reason, and says for each whether it gets a decision record. If any does, it raises starting one (the repo has no docs/adr/), recommending an answer; "none" is acceptable where the request itself settled the lasting shape and only transitional choices remain.
- Questions, if any, are at most three, each with a recommended answer.
