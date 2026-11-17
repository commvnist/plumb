---
name: plumb-audit
description: Read-only health report on a codebase, an area of it, or its test suite, ranked by what to fix first. Use for "audit this repo", "tech debt", "security check", "what can I delete", "audit the tests", "prune the tests", "find test gaps". For a diff, branch or pull request, use plumb-review.
---

# Plumb: audit

An audit changes nothing. Mode: `code`, `tests` or `both`. For a repository too large for one session, run one plumb-auditor agent per area and merge and re-rank their findings; say which you did, or why it fits one session.

Code mode: bugs the system can actually produce, security holes, leaked secrets (location, never value), untested logic, dead code. Tests mode: load plumb-test, classify each test by its "Keep, merge, rewrite or delete", and find gaps by risk, not coverage.

## Output

- **Fix first:** <findings: at most 15, ranked, then "N more on request">
- **Delete:** <items>
- **Tests:** keep <n> · merge <n> · rewrite <n> · delete <n> · gaps <n>
- **Verified:** <what you ran> → <result>

No generic advice.
