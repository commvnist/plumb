---
type: regex
pattern: '(FAIL|ERROR): test_\w+ \(|FAILED \S+::'
match: contains
target: trace
---
