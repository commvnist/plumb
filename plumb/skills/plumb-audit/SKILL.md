---
name: plumb-audit
description: One-shot, read-only health report on a codebase or its test suite, ranked by what to fix first. Code mode finds bugs, risks, dead code and over-engineering. Tests mode prunes useless tests and finds missing ones by risk. Changes nothing. Use for "audit this repo", "tech debt", "what can I delete", "audit the tests", "prune the tests", "find test gaps", "is our suite any good".
---

# Plumb: audit

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

An audit leaves the code exactly as it found it. It returns a ranked list the user can act on one diff at a time.

**Mode:** `code` (the default), `tests`, or `both`. Use what the user named; otherwise infer it from their words. For a large repository, split it into areas and run one plumb-auditor agent per area in parallel, then merge, deduplicate and re-rank their findings.

## Code mode

Look for:
1. **Correctness:** bugs with a concrete failing scenario.
2. **Safety:** security holes, data loss, leaked secrets or personal data, unsafe handling of untrusted input.
3. **Failure handling:** swallowed errors, fake defaults, failures nobody would ever see.
4. **Behaviour under real conditions:** what breaks with load, slowness, repetition or concurrency.
5. **Risky code with no proof:** important logic that nothing tests.
6. **Deletion:** dead code, unused options, abstractions with a single use, duplicated helpers, needless dependencies.
7. **Inconsistency:** several ways of doing the same thing, where one should win.
8. **Docs that lie:** comments and documentation the code contradicts.

## Tests mode

**Prune.** Classify each test, or each cluster of similar tests:
- **Keep:** meets the plumb-test standard.
- **Merge:** near-duplicates that should become one table-driven test.
- **Rewrite:** guards the right behaviour in a brittle way, through internals, heavy fakes or sleeps.
- **Delete:** matches plumb-test's "Reject on sight" or "No test" list, or can't fail. Never break code to prove a test can't fail: name the break it would miss and mark it "can't fail (unconfirmed)". Proving it is a follow-up the user can pick.

**Find gaps** from risk, not from coverage numbers. List the behaviours that matter (from callers, business rules, input boundaries, bug history in version control, areas that keep breaking), map each to the tests that would catch a realistic break, and report the high-risk behaviours that have none. Coverage tools may suggest where to look; they never decide.

## Output

```
Scope:  <what was audited>   Mode: <mode>

Fix first:
1. <location> — <finding> — <concrete consequence> — action: <what to do> — ~<n> lines
2. …
3. …

Then:
4. …   (at most 15 findings in total, ranked)

Delete: <items> — ~<lines removed in total>
Tests:  keep <n> · merge <n> · rewrite <n> · delete <n> · gaps <n>   (tests mode)
Not examined: <areas skipped, and why>
```

Rank by consequence per line of fix. Every finding is concrete and specific to this code. No generic advice. End with: "Pick any number and each lands as its own diff."
