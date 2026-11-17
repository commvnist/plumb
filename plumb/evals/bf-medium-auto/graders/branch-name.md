---
type: regex
pattern: 'git (checkout -b|switch -c|branch) +(feat|fix|perf|refactor|style|test|docs|build|ci|chore|revert)/[a-z0-9-]+'
match: contains
target: trace
---
