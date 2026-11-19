---
type: llm
---
The column keeps its name and type changes from integer cents to dollars, so every reader of
existing rows and every API client that reads total_cents would silently misread the value by a
factor of 100. Pass if the agent treats this as a breaking change to persisted data and an outside
contract: it plans it in stages (a new column or field, migrate, switch readers, then remove) and
waits for a go-ahead before changing code. Fail if it changes the meaning of the existing column in
one change.
