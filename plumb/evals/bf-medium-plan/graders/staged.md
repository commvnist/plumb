---
type: llm
---
The column is persisted data, so old and new code will read it during a deploy. Pass if the plan
stages it (add the new column, migrate or dual-write, then remove the old) across separate diffs or
releases, with migrations in app/migrations/ as the project's rules require. Fail if one diff or one
release both adds the new column and drops the old one.
