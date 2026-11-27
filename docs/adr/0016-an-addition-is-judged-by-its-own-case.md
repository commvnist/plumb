# 16. An addition is judged by its own case

## Status

Accepted. Amends [ADR 10](0010-skill-text-and-its-eval-live-and-die-together.md), [ADR 14](0014-the-gate-fits-the-change.md) and [ADR 15](0015-the-fast-tier-is-the-default-gate.md).

## Context

ADR 14 gated a new feature by cases written for it, but still decided "a rewording, addition or trim in text existing cases guard" against main, and ADR 15's fast tier carried that out: a unit that grew around a guarded phrase made the existing case a deciding one, on which the addition had to beat main. Those cases were written for the text that was already there. An addition they don't grade can only tie main on them, so it was dropped for failing a test that never asked about it, while the same text added as a unit of its own, with a case written for it, would have landed as a feature. Where the words sat decided the gate, not what they added.

commvnist set the rule on 2026-11-27: beating main on existing evals only makes sense for rewordings of behaviour those evals already cover; a new feature or addition is judged by new targeted evals written for it (does it do what it promises, no regression nearby), and is never dropped for failing to beat evals that didn't cover it.

## Decision

- **An addition is gated like a feature,** wherever it sits: a case written for what it adds, new with the change, passes each check in at least two thirds of runs on each model on the new arm, and the existing cases guarding the unit it grew hold against main. Without such a case the addition is owed one, and lands only under ADR 12's conditions meanwhile.
- **Existing cases on changed text hold.** A rewording or trim lands when they hold against main. Only a rewording meant to change behaviour those cases grade must beat main on them, by the evals README's decision rule.
- The fast tier has no tier that makes an addition beat main: `_fast/affected.py` selects existing cases on any changed unit as holds, a case new with the change on new or grown text as a feature, and reports grown text no new case guards as owed. `_fast/run.py` prints every hold as a guard, and the cases on reworded or cut units also as a decision, so a rewording meant to improve reads its verdict from the same runs; an addition's held cases get no such verdict to misread.

## Consequences

- An addition costs a case written for it, which is the evidence that it does what it says; existing cases no longer stand in for that.
- An addition whose own case passes on main as well still lands; the case becomes its baseline, as ADR 14 says of features, and the operator's ask or the failure it answers is the reason it exists.
