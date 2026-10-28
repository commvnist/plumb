---
name: plumb-audit
description: One-shot, read-only health report on a codebase or its test suite, ranked by what to fix first. Code mode finds bugs, risks, dead code and over-engineering. Tests mode prunes useless tests and finds missing ones by risk. Changes nothing. Use for "audit this repo", "tech debt", "what can I delete", "audit the tests", "prune the tests", "find test gaps", "is our suite any good".
---

# Plumb: audit

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

An audit changes nothing in the repository or in any shared or production system, not even briefly, and adds no files to it beyond the ignored output of running its checks; mark a test you suspect can't fail, but could confirm only by breaking code, as "can't fail (unconfirmed)". It returns a ranked list the user can act on one diff at a time.

**Mode:** `code` (the default), `tests`, or `both`. Use what the user named; otherwise infer it from their words. For a large repository, split it into areas and run one plumb-auditor agent per area in parallel, then merge, deduplicate and re-rank their findings, dropping any Delete whose covering test another area also deletes or merges, and any gap another area's tests already catch.

## Code mode

Look for:
1. **Correctness:** bugs with a concrete failing scenario, traced through the code or reproduced without editing it; say so in the finding if you couldn't confirm it.
2. **Safety:** security holes, data loss, leaked secrets or personal data (cite the location, never the value; a live secret's action is rotate, then remove), unsafe handling of untrusted input.
3. **Failure handling:** swallowed errors, fake defaults, failures nobody would ever see.
4. **Behaviour under real conditions:** what breaks with load, slowness, repetition or concurrency.
5. **Risky code with no proof:** important logic that nothing tests.
6. **Deletion:** dead code and unused options (check indirect users as plumb-refactor step 2 does; anything outside consumers can reach is an interface change, not dead), abstractions with a single use, duplicated helpers, needless dependencies.
7. **Inconsistency:** several ways of doing the same thing, where one should win.
8. **Docs that lie:** comments and documentation the code contradicts.

## Tests mode

**Prune.** Load plumb-test if it isn't loaded; its standard decides each class. Classify each test, or each cluster of similar tests. Treat any test the suite has stopped trusting (failing, skipped or quarantined because it failed, retried, or flaky) as a finding: classify it like any other test; for one worth keeping, the action removes the cause at its source: nondeterminism in the test itself (plumb-test, as Rewrite), or the code bug it caught, a race in the code included (plumb-debug, ranked as a correctness finding). Never delete it just for being flaky.
- **Keep:** none of the below applies. Style flaws alone are not a finding.
- **Merge:** near-duplicates, including table rows that catch the same break, that should become one table-driven test or one row, or a cluster of fake-heavy tests that one test at the right level would replace.
- **Rewrite:** guards the right behaviour badly: brittle (it would fail on a change that preserves the behaviour) blind (it would pass with the break it exists to catch), or slow where a cheaper real level would catch the same break.
- **Delete:** guards no behaviour worth keeping: the behaviour behind it, judged apart from what the test happens to assert, fails any of plumb-test's three conditions (nobody relies on it, no nameable break, or other tests or checks already catch every realistic break in it; of overlapping tests, keep the one that best meets the standard). Before calling a break unnameable, read the commit that added the test; a test that landed with a fix names its break there. A test whose behaviour meets all three is never Delete, even if it matches "Reject on sight" or "No test" or can't fail: keep it if it is sound and asserts that behaviour where a caller sees it, otherwise Merge or Rewrite.

**Find gaps** from risk, not from coverage numbers. List the behaviours that matter (from callers, business rules, input boundaries, bug history in version control, areas that keep breaking), map each to the tests or checks that would catch a realistic break, and report the high-risk behaviours that have none. Coverage tools may suggest where to look; they never decide.

## Output

```
Scope:  <what was audited>   Mode: <mode>

Fix first:
1. <location> — <finding> — <concrete consequence> — action: <what to do> — ~<n> lines
2. …
3. …

Then:
4. …   (at most 15 findings in total, ranked; if there are more, end with "N more on request")

Delete: <items> — ~<lines removed in total>
Tests:  keep <n> · merge <n> · rewrite <n> · delete <n> · gaps <n>   (tests mode)
Not examined: <areas skipped, and why>
```

Rank by consequence per line of fix. Every finding is concrete and specific to this code. No generic advice. End with: "Pick any number and each lands as its own diff."
