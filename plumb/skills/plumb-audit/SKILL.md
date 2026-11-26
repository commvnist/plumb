---
name: plumb-audit
description: Read-only health report on a codebase, an area of it, or its test suite, ranked by what to fix first. Use for "audit this repo", "tech debt", "security check", "what can I delete", "audit the tests", "prune the tests", "find test gaps". For a diff, branch or pull request, use plumb-review.
---

# Plumb: audit

An audit changes nothing. Mode: `code`, `tests` or `both`. For a repository too large for one session, run the project's checks once, then one plumb-auditor agent per area with its area's results, and merge and re-rank their findings; say which you did, or why it fits one session.

Code: bugs the system can actually produce, security holes, traced from where untrusted input enters (a check the code needs and lacks is a finding, never an unchecked area), leaked secrets (location, never value), dependencies the project can't vouch for (known-vulnerable, unmaintained, unpinned), untested logic, dead code. Tests: load plumb-test, classify each test by plumb-test's "Keep, merge, rewrite or delete", and find gaps by risk, not coverage, each shown where it can be by a realistic break the suite stays green on, tried in a scratch copy.

## Output

- **Fix first:** <findings, at most 15, ranked, then "N more on request">
- **Delete:** <items, each with the search that shows it unused and what that search can't see>
- **Tests:** keep <n> · merge <n> · rewrite <n> · delete <n> · gaps <n>
- **Verified:** <command> → <result>; unchecked: <what the audit didn't reach>

No generic advice.
