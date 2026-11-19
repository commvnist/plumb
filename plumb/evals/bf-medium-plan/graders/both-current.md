---
type: llm
---
Pass if, while the old and new columns both exist, the plan keeps both current (writing both, or a
trigger or backfill that keeps them in step) so code of either version reads correct data, and
removes the old column only after no deployed code reads it.
