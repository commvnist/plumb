# 13. The fast tier is the default gate

## Status

Accepted. Amends [ADR 10](0010-skill-text-and-its-eval-live-and-die-together.md) and [ADR 12](0012-a-wording-can-land-on-principle.md).

## Context

Every wording change was gated by running much of the suite: guard runs of all 40 built cases on two models, the fixture cases beside them, both arms at 6 to 18 runs, and the routing probe. Most of those sessions asked cases the change could not reach, and main's arm was run again for every candidate on the same main. commvnist asked on 2026-11-27 for a gate that spends tokens only where a change can show, and for it to be the default from then on.

The regressions earlier gates caught sat in two places: in a case guarding the changed text or text that points at it by number (review-voice, bf-medium-auto), and in a case that loads the changed skill or the skill that dispatches the changed agent without guarding the changed line (flaky-commit, pr-rename, bf-large-audit-all).

## Decision

Each change to plumb's text is gated by `plumb/evals/_fast/run.py`: the static checks, then the cases `_fast/affected.py` selects (those guarding a changed unit decide it; those guarding a unit it points at or that points at it, and outside the charter those loading the changed skill or its dispatcher, guard it), and the routing probes a changed description can move, all under the decision rule in `plumb/evals/README.md`. Main's runs are kept by the hash of main's text and reused while it is unchanged. The whole suite runs only when the selection covers most of it, or the operator asks.

## Consequences

- A gate costs the cases a change can reach, not the suite: a change to one skill's step asks one to two dozen cases instead of about a hundred, and a second wording on the same main pays only for its own arm.
- A regression in a case that neither guards linked text nor loads the changed file goes unseen until a full run. A charter change selects by its rule and the text pointing at it, never by loading, since every case loads the charter.
- `scripts/test_fast_select.py` replays each regression past gates caught and fails when the selection would miss it; a regression found later that the selection missed is added there with the rule that catches it.
