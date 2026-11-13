---
name: plumb-audit
description: One-shot, read-only health report on a codebase or its test suite, ranked by what to fix first. Use for "audit this repo", "tech debt", "what can I delete", "audit the tests", "prune the tests", "find test gaps".
---

# Plumb: audit

An audit changes nothing. Mode: `code`, `tests` or `both`. For a repository too large for one session, run one plumb-auditor agent per area and merge their findings; say which you did, or why it fits one session.

Code mode: bugs the system can actually produce, security holes, leaked secrets (location, never value), untested logic, dead code. Tests mode: classify each test by plumb-test's "Keep, merge, rewrite or delete", and find gaps by risk, not coverage.

## Output

```
Fix first:
1. <location> — <finding> — <consequence> — action: <what to do>
Then: …   (at most 15, ranked; then "N more on request")
Delete: <items>
Tests:  keep <n> · merge <n> · rewrite <n> · delete <n> · gaps <n>
```

No generic advice. A defect repeated across locations is one finding that lists them.
