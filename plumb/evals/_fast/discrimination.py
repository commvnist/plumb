"""Which graders can't tell plumb from no plumb, read from a `claude plugin eval --ablation with-without --json` run.

  python3 _fast/discrimination.py <run.json> [<run.json> ...]

A grader whose runs without plumb pass as often as its runs with it can't show a regression in plumb: either both
arms pass (the case tests the model) or both fail (plumb fails it too, or the grader can't pass anything). Several
files from one model are read together; give each model's files in a separate call, since a pass on one model
says nothing about another. Graders that only guard a limit (`tool_used` with a maximum) are left out: they are
meant to pass in both arms, and so are runs that ended in an error, which are rerun rather than
scored. Exit status is 0; the listing is for a person deciding which cases to rebuild.
"""
import json
import sys


def tallies(paths):
    """{(case, grader): {"with": [bools], "without": [bools], "type": str}} over every scored run."""
    found = {}
    for path in paths:
        with open(path) as f:
            run = json.load(f)
        for case in run["cases"]:
            types = {g["name"]: (g["type"], g.get("config") or {}) for g in case["graders"]}
            for arm in ("with", "without"):
                for result in case["arms"].get(arm, []):
                    if result.get("error"):
                        continue  # an environment failure, rerun rather than scored (evals README)
                    for g in result["graders"]:
                        if not g.get("scored", True):
                            continue
                        kind, config = types.get(g["name"], ("?", {}))
                        if kind == "tool_used" and config.get("max") is not None:
                            continue  # a limit both arms should keep
                        entry = found.setdefault((case["name"], g["name"]), {"with": [], "without": [], "type": kind})
                        entry[arm].append(bool(g["passed"]))
    return found


def main(paths):
    rows = []
    for (case, grader), t in sorted(tallies(paths).items()):
        w, o = t["with"], t["without"]
        if not w or not o or sum(o) / len(o) < sum(w) / len(w):
            continue
        both = ("both pass" if all(w) and all(o) else "both fail" if not any(w) and not any(o)
                else "no plumb ahead" if sum(o) / len(o) > sum(w) / len(w) else "tied")
        rows.append(f"{both:15} {case:28} {grader:18} {t['type']:10} with {sum(w)}/{len(w)}  without {sum(o)}/{len(o)}")
    print("\n".join(rows) if rows else "every grader passes more often with plumb")
    print(f"{len(rows)} grader(s) don't tell plumb from no plumb")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
