---
name: plumb-audit
description: One-shot, read-only health report on a codebase or its test suite, ranked by what to fix first. Code mode finds bugs, risks, dead code and over-engineering. Tests mode prunes useless tests and finds missing ones by risk. Changes nothing. Use for "audit this repo", "tech debt", "what can I delete", "audit the tests", "prune the tests", "find test gaps", "is our suite any good".
---

# Plumb: audit

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

An audit changes nothing in the repository or in any shared or production system, not even briefly; mark a test you suspect can't fail, but could confirm only by breaking code, as "can't fail (unconfirmed)". It returns a ranked list the user can act on one diff at a time.

**Mode:** `code` (the default), `tests`, or `both`. Use what the user named; otherwise infer it from their words. For a repository too large to read closely in one session, split it into areas, each some code together with its tests, run the project's checks once yourself, then run one plumb-auditor agent per area in parallel, giving each what ran and what failed in its area, since a suite run per auditor multiplies the cost and the failures that come from runs colliding. Then merge, deduplicate and re-rank their findings, dropping any Delete whose covering test another area also deletes or merges, and any gap another area's tests already catch. With agents off (the charter's Agents), audit the areas one at a time yourself, keeping only each area's ranked findings before starting the next, so the context holds findings rather than files.

## Code mode

Look for:
1. **Correctness:** bugs with a concrete failing scenario the system can produce (its input traced back to where it enters, since a state the code is never given asks for a guard charter rule 8 forbids), traced through the code or reproduced without editing it; say so in the finding if you couldn't confirm it.
2. **Safety:** security holes, data loss, leaked secrets or personal data (cite the location, never the value; a live secret's action is rotate, then remove), unsafe handling of untrusted input.
3. **Failure handling:** swallowed errors, fake defaults, failures nobody would ever see.
4. **Behaviour under real conditions:** what breaks with load, slowness, repetition or concurrency.
5. **Risky code with no proof:** important logic that nothing tests.
6. **Deletion:** dead code and unused options, abstractions with a single use, duplicated helpers, needless dependencies. Check history, decision records and indirect users first (dynamic lookup, configuration, serialised data): anything outside consumers can reach is an interface, not dead, and something a record says was chosen on purpose is reported with that record's reason, not as over-engineering.
7. **Inconsistency:** several ways of doing the same thing, where one should win.
8. **Docs that lie:** comments, documentation and accepted decision records the code contradicts.

## Tests mode

**Prune.** Classify each test, or each cluster of similar tests, as plumb-test's "Keep, merge, rewrite or delete" says. A test the suite has stopped trusting (failing, skipped, quarantined, retried or flaky) is a finding, classified like any other; for one worth keeping, the action removes the cause at its source, in the test or in the code bug it caught. Never delete it just for being flaky.

**Find gaps** from risk, not from coverage numbers. List the behaviours that matter (from callers, business rules, input boundaries, bug history, areas that keep breaking), map each to the tests or checks that would catch a realistic break, and report the high-risk behaviours that have none.

## Output

```
Scope:  <what was audited, and the areas it was split into or why it wasn't>   Mode: <mode>

Fix first:
1. <location> — <finding> — <concrete consequence> — action: <what to do> (<principle>) — ~<n> lines
2. …
3. …

Then:
4. …   (at most 15 findings in total, ranked; if there are more, end with "N more on request")

Delete: <items> — ~<lines removed in total>
Tests:  keep <n> · merge <n> · rewrite <n> · delete <n> · gaps <n>   (tests or both)
Not examined: <areas skipped, and why>
```

Rank by consequence per line of fix. Every finding is concrete and specific to this code; no generic advice. A defect repeated across locations or areas is one finding that lists them (or gives the search that finds them all), ranked by their combined consequence, with its action at the shared cause where there is one, since a ranked list filled by one pattern hides the next problem. End with: "Pick any number and each lands as its own diff." Land picks as plumb-build applies accepted suggestions (plumb-debug for a bug).
