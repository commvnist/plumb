# 15. The fast tier is the default gate

## Status

Accepted. Amends [ADR 10](0010-skill-text-and-its-eval-live-and-die-together.md) and [ADR 12](0012-a-wording-can-land-on-principle.md); carries out [ADR 14](0014-the-gate-fits-the-change.md)'s gate for each kind of change. Amended by [ADR 16](0016-an-addition-is-judged-by-its-own-case.md): no case makes an addition beat main.

## Context

Every wording change was gated by running much of the suite: guard runs of all 40 built cases on two models, the fixture cases beside them, both arms at 6 to 18 runs, and the routing probe. Most of those sessions asked cases the change could not reach, and main's arm was run again for every candidate on the same main. commvnist asked on 2026-11-27 for a gate that spends tokens only where a change can show, and for it to be the default from then on.

The regressions earlier gates caught sat in two places: in a case guarding the changed text or text that points at it by number (review-voice, bf-medium-auto), and in a case that loads the changed skill or the skill that dispatches the changed agent without guarding the changed line (flaky-commit, pr-rename, bf-large-audit-all).

## Decision

Each change to plumb's text is gated by `plumb/evals/_fast/run.py`: the static checks, then the cases `_fast/affected.py` selects, and the routing probes a changed description can move. A case guarding a changed unit answers the question its kind of change asks, as ADR 14 sets out: a case written for text main lacks shows the feature works, on the new arm alone; one guarding a unit that grew must see the addition beat main; one guarding a unit reworded or cut must hold. Cases guarding a unit the change points at or that points at it, and outside the charter those loading the changed skill or its dispatcher, are guards. New or grown text no case guards is reported as owed a case. Main's runs are kept by the hash of main's text and reused while it is unchanged. The whole suite runs only when the selection covers most of it, or the operator asks.

## Consequences

- A gate costs the cases a change can reach, not the suite: replayed over the 16 changes to the text before this record, the median selection was a quarter of the 101 cases (1 for a charter rule, 46 for plumb-build, which most cases load), and a second wording on the same main pays only for its own arm.
- A regression in a case that neither guards linked text nor loads the changed file goes unseen until a full run. A charter change selects by its rule and the text pointing at it, never by loading, since every case loads the charter.
- `scripts/test_fast_select.py` replays each regression past gates caught and fails when the selection would miss it; a regression found later that the selection missed is added there with the rule that catches it.
