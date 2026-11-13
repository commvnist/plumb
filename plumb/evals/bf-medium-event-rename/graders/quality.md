---
type: llm
---
The publisher and the consumer live in the same repository, but messages already queued, and the
two sides running different versions during a deploy, will meet the renamed field. Pass if the agent
stages the rename (for example the consumer accepts both names first, then the publisher switches,
then the old name is dropped) or plans it before changing code, or otherwise names that old and new
versions will read each other's messages. Fail if it renames both sides in one diff and says nothing
about messages in flight or deploy order.
