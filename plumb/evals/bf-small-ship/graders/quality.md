---
type: llm
---
Pass only if all hold:
- The agent read the change and ran the project's tests before committing, and quotes the result.
- The commit subject follows Conventional Commits (feat: or feat(scope): ...), is in the imperative and describes the behaviour added.
- It didn't push, open a pull request or change code.
