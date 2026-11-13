---
name: plumb-audit
description: One-shot, read-only health report on a codebase or its test suite, ranked by what to fix first. Code mode finds bugs, risks, dead code and over-engineering. Tests mode prunes useless tests and finds missing ones by risk. Changes nothing. Use for "audit this repo", "tech debt", "what can I delete", "audit the tests", "prune the tests", "find test gaps", "is our suite any good".
---

# Plumb: audit

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

An audit changes nothing. It returns a ranked list the user can act on one diff at a time. Mode: `code` (the default), `tests` or `both`. For a repository too large to read closely in one session, run one plumb-auditor agent per area in parallel and merge their findings; say which you did, or why it fits one session.

**Code mode** looks for bugs with a concrete scenario the system can produce, security holes and leaked secrets (the location, never the value), swallowed errors, untested important logic, dead code and duplication. **Tests mode** classifies each test as plumb-test's "Keep, merge, rewrite or delete" says, and finds gaps from risk, not coverage.

## Output

```
Scope: <what was audited>   Mode: <mode>
Fix first:
1. <location> — <finding> — <concrete consequence> — action: <what to do> — ~<n> lines
Then:
4. …   (at most 15 findings, ranked; then "N more on request")
Delete: <items>
Tests:  keep <n> · merge <n> · rewrite <n> · delete <n> · gaps <n>
```

Rank by consequence per line of fix. No generic advice. A defect repeated across locations is one finding that lists them.
