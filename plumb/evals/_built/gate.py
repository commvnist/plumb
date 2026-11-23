"""Reads run.py results and says, for each check, what the gate decides and what to run next.

  python3 _built/gate.py <results.json> [<results.json> ...] [--main main] [--new new]

Give one results file per agent model (each run.py run writes its model into every result). Models are kept
apart: each has its own pass rate, so they are never pooled into one count.

Two questions, in this order:

1. Does the case reproduce the failure? Main must fail a check at least twice in its first six measured runs
   on a model. If it doesn't, the answer is "case didn't reproduce": the case is too easy, too short or on the
   wrong model to show the failure the reviewers saw, so it says nothing about the wording, and the item stays
   open with the case marked for a harder one. Only models where the case reproduces go on to question 2.
2. Does the wording beat main? An exact test stratified by model (each model's runs compared only with its
   own, the conditional form of Cochran-Mantel-Haenszel), one-sided. The wording lands at p <= 0.05. Runs go
   in stages of 6, 18 and 30 per arm per model: a candidate ahead of main is run on to the next stage; one no
   better than main is dropped from 18 runs on (at 6 it stays open: too few runs to drop it); at 30 anything not
   landed is dropped as undecided, with the power the runs had to find a gain. When both arms fail every run,
   the grader is checked on a known-good output before the wording is called ineffective.

The first six main runs both decide that a case reproduces and count in the comparison, and each stage is a
fresh look at the data; a simulation of a wording with no effect put the chance of a false landing at 4% to 7%
against the nominal 5% when main passes at most 60% of runs, up to 8% at 80%, which this rule accepts.

With --guard, every check is read as a guard: it fell when main beats the change at p <= 0.05, and it holds
once each arm has 18 runs per model without that. A trim is a guard question on its deciding cases.
"""
import argparse
import json
from math import comb

REPRODUCE_RUNS, REPRODUCE_FAILS = 6, 2
STAGES = (6, 18, 30)
ALPHA = 0.05


def hypergeom(k, total, n_new, n_main):
    """P(new arm holds k of `total` passes) when passes fall at random between the arms."""
    if k < 0 or k > n_new or total - k < 0 or total - k > n_main:
        return 0.0
    return comb(n_new, k) * comb(n_main, total - k) / comb(n_new + n_main, total)


def stratified_p(strata):
    """One-sided exact p that the new arm's passes, summed over models, are this high or higher by chance.

    `strata` holds (main passes, main runs, new passes, new runs) per model."""
    dist = {0: 1.0}
    for a, n, b, m in strata:
        total = a + b
        step = {k: hypergeom(k, total, m, n) for k in range(0, m + 1)}
        nxt = {}
        for s, ps in dist.items():
            for k, pk in step.items():
                if pk:
                    nxt[s + k] = nxt.get(s + k, 0.0) + ps * pk
        dist = nxt
    observed = sum(b for _, _, b, _ in strata)
    return sum(p for s, p in dist.items() if s >= observed)


def power(n, base=0.5, gain=0.9, alpha=ALPHA):
    """Chance that n runs per arm on one model find a true rise from `base` to `gain`."""
    def binom(k, p):
        return comb(n, k) * p ** k * (1 - p) ** (n - k)
    return sum(binom(a, base) * binom(b, gain) for a in range(n + 1) for b in range(n + 1)
               if stratified_p([(a, n, b, n)]) <= alpha)


def tally(results, main, new):
    """{(case, check): {model: {arm: [bool, ...]}}}, measured runs only, in run order."""
    rows, texts = {}, {}
    for r in results:
        if r["arm"] in (main, new) and "text" in r:
            texts.setdefault((r["case"], r.get("model", "?"), r["arm"]), set()).add(r["text"])
    mixed = sorted(k for k, v in texts.items() if len(v) > 1)
    if mixed:
        raise SystemExit("results from different plugin texts share an arm name; pass one arm's files at a time: "
                         + "; ".join(f"{c} on {m}, arm {a}" for c, m, a in mixed))
    for r in sorted(results, key=lambda r: r["run"]):
        for check, ok in r["checks"].items():
            if ok is not None and r["arm"] in (main, new):
                rows.setdefault((r["case"], check), {}).setdefault(r.get("model", "?"), {}) \
                    .setdefault(r["arm"], []).append(ok)
    return rows


def decide(by_model, main, new):
    reproduced, notes = {}, []
    for model, arms in sorted(by_model.items()):
        first = arms.get(main, [])[:REPRODUCE_RUNS]
        if len(first) < REPRODUCE_RUNS:
            notes.append(f"{model}: main {sum(first)}/{len(first)}, needs {REPRODUCE_RUNS} measured runs")
        elif len(first) - sum(first) < REPRODUCE_FAILS:
            notes.append(f"{model}: main {sum(first)}/{len(first)}, case didn't reproduce")
        else:
            reproduced[model] = arms
    if not reproduced:
        return "case didn't reproduce" if notes and all("reproduce" in n for n in notes) else "run main", notes
    strata, cells = [], []
    for model, arms in reproduced.items():
        a, b = arms.get(main, []), arms.get(new, [])
        if not b:
            cells.append(f"{model}: main {sum(a)}/{len(a)}, reproduces")
            continue
        strata.append((sum(a), len(a), sum(b), len(b)))
        cells.append(f"{model}: main {sum(a)}/{len(a)} new {sum(b)}/{len(b)}")
    if not strata:
        return "reproduces; gate the wording", notes + cells
    p = stratified_p(strata)
    n = min(min(s[1], s[3]) for s in strata)
    ahead = sum(s[2] / s[3] for s in strata) > sum(s[0] / s[1] for s in strata)
    cells.append(f"p = {p:.3f}")
    if p <= ALPHA:
        return "land", notes + cells
    if all(s[0] == 0 and s[2] == 0 for s in strata):
        return "check the grader: both arms fail every run; run a known-good output through it", notes + cells
    if n >= STAGES[-1]:
        return f"drop: undecided at {n} (power for 50%->90% was {power(n):.0%})", notes + cells
    if not ahead and n >= STAGES[1]:
        return "drop: no better than main", notes + cells
    if not ahead:
        return f"open: not ahead at {n} runs, too few to drop; run each arm to {STAGES[1]}", notes + cells
    nxt = next(s for s in STAGES if s > n)
    return f"run each arm to {nxt}", notes + cells


def guard(by_model, main, new):
    """Whether a guard check fell: main ahead of the change at p <= 0.05. No reproduce step: a guard is meant to
    pass on main. A trim is judged this way on its deciding cases, with the trimmed text as `new`."""
    strata, cells = [], []
    for model, arms in sorted(by_model.items()):
        a, b = arms.get(main, []), arms.get(new, [])
        if a and b:
            strata.append((sum(b), len(b), sum(a), len(a)))
            cells.append(f"{model}: main {sum(a)}/{len(a)} new {sum(b)}/{len(b)}")
    if not strata:
        return "run both arms", cells
    p = stratified_p(strata)
    n = min(min(s[1], s[3]) for s in strata)
    cells.append(f"p (main ahead) = {p:.3f}")
    if p <= ALPHA:
        return "fell", cells
    if n < STAGES[1]:
        return f"holds so far; run each arm to {STAGES[1]} before relying on it", cells
    return "holds", cells


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results", nargs="+")
    ap.add_argument("--main", default="main")
    ap.add_argument("--new", default="new")
    ap.add_argument("--guard", action="store_true", help="read every check as a guard: did the change lower it?")
    a = ap.parse_args()
    results = []
    for path in a.results:
        with open(path) as f:
            results += json.load(f)
    for (case, check), by_model in sorted(tally(results, a.main, a.new).items()):
        verdict, detail = (guard if a.guard else decide)(by_model, a.main, a.new)
        print(f"{case:18} {check:18} {verdict}\n{'':38}" + "; ".join(detail))


if __name__ == "__main__":
    main()
