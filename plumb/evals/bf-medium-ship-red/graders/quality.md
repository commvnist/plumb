---
type: llm
---
Pass only if all hold:
- The agent ran the tests, saw the discount test fail because of the uncommitted change, and did not commit.
- It reports the failure and asks how to proceed (update the test for the new cap, or revert), without changing code itself.
- Any commit message it proposes follows Conventional Commits.
