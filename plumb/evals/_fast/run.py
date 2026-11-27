"""The fast eval tier, the default gate for a change to plumb's text: static checks, then only the cases and
routing probes _fast/affected.py selects, the new wording against main, decided by _built/gate.py.

  python3 _fast/run.py --judge <the strongest model> [--base origin/main] [--runs 6] \
      [--model claude-haiku-5-5 --model claude-sonnet-5-5] [--baseline DIR] [--dry-run]

Run from plumb/evals. Main is the plugin text at --base; new is the working tree. Both arms run the working
tree's cases, so a case changed with the wording judges both the same way.

Main's runs are kept under --baseline by the hash of main's text, per model and case, and reused while that
text is unchanged: a wording gated after another on the same main pays only for its own arm. A case whose
definition changed since its baseline was recorded is run on both arms again.

Each stage is one call: run at 6, read the verdicts, and call again with --runs 18 (the extra runs are added
to the earlier ones) where gate.py says to run on. The verdicts follow plumb/evals/README.md: deciding cases
by the decision rule, guard cases by gate.py --guard. Nothing here changes the bar a wording must clear; it
changes which cases are asked.

--dry-run prints the selection and the number of agent sessions it would start, and starts none; with --judge it
also counts the earlier runs it would reuse.
"""
import argparse
import glob
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.dirname(HERE)
PLUGIN = os.path.dirname(EVALS)
ROOT = os.path.dirname(PLUGIN)
MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5"]
STATIC = [["python3", "scripts/lint_skills.py"], ["python3", "scripts/check_refs.py"],
          ["python3", "plumb/evals/_fixtures/write_cases.py", "--check"], ["python3", "scripts/test_lint_skills.py"],
          ["python3", "scripts/test_fast_select.py"],
          ["python3", "scripts/test_graders.py"]]
SUITE_TOOLS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Skill"]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


affected = load("affected", os.path.join(HERE, "affected.py"))
built = load("built_run", os.path.join(EVALS, "_built", "run.py"))


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=kw.pop("cwd", ROOT), text=kw.pop("text", True), **kw)


def static():
    """Runs every static check; returns the ones that failed."""
    failed = []
    for cmd in STATIC:
        cwd = os.path.join(ROOT, "plumb", "evals") if "write_cases.py" in cmd[1] else ROOT
        args = [cmd[0], os.path.relpath(os.path.join(ROOT, cmd[1]), cwd)] + cmd[2:]
        done = sh(args, cwd=cwd, capture_output=True)
        print(f"{'ok  ' if done.returncode == 0 else 'FAIL'} {' '.join(cmd)}")
        if done.returncode:
            print((done.stdout + done.stderr).strip())
            failed.append(" ".join(cmd))
    return failed


def main_arm(base, into):
    """A plugin directory holding the text at `base` and the working tree's cases."""
    os.makedirs(into)
    archive = sh(["git", "archive", "--format=tar", base, "plumb"], capture_output=True, text=False, check=True)
    sh(["tar", "-x", "-C", into], input=archive.stdout, text=False, check=True)
    plugin = os.path.join(into, "plumb")
    shutil.rmtree(os.path.join(plugin, "evals"))
    shutil.copytree(EVALS, os.path.join(plugin, "evals"), ignore=shutil.ignore_patterns("results", "__pycache__"))
    return plugin


# Code every case's runs depend on besides its own definition: the fixtures and the runners that grade them.
SHARED = ["_fixtures/make.py", "_fixtures/seed.sh"]
BUILT_CODE = ["_built/run.py", "_built/sim.py", "_built/probe_carrier.py", "_built/probe_framing.py", "_harm/run.py",
              "_fixtures/write_cases.py"]  # many built cases take their prompts and scaffolds from the suite table


def case_hash(case):
    """A hash of what a case's runs depend on, so runs recorded under another definition aren't reused.

    A built case's checks are functions that call helpers anywhere in the runner, so the runner's files stand
    for its definition; a suite case is its generated folder."""
    h = hashlib.sha256(case.encode() + b"\0")
    if case.startswith("_built/"):
        paths = [os.path.join(EVALS, p) for p in BUILT_CODE]
    else:
        paths = sorted(p for p in glob.glob(os.path.join(EVALS, case, "**", "*"), recursive=True) if os.path.isfile(p))
    for path in paths + [os.path.join(EVALS, p) for p in SHARED]:
        h.update(os.path.relpath(path, EVALS).encode() + b"\0" + open(path, "rb").read())
    return h.hexdigest()[:12]


def suite_results(report, arm, text, model, first=1):
    """gate.py records from a `claude plugin eval --json` report: one per run, each grader a check."""
    records = []
    for case in report["cases"]:
        for n, run in enumerate(case["arms"].get("with", []), first):
            failed = bool(run.get("error"))
            records.append({"case": case["name"], "arm": arm, "text": text, "run": n, "model": model,
                            "env_failure": failed, "cost": run.get("costUsd") or 0,
                            "checks": {} if failed else {g["name"]: g["passed"] for g in run.get("graders", [])
                                                         if g.get("scored", True) or g["name"].startswith("skill-")}})
    return records


def run_suite_case(case, arm, plugin, model, judge, runs, out, first):
    path = os.path.join(out, f"{case}-{arm}-{first}.json")
    sh(["claude", "plugin", "eval", plugin, "--ablation", "none", "--model", model, "--judge-model", judge,
        "--case", case, "--runs", str(runs), "-j", "6", "--scaffold", "--trust-plugin", "--no-publish",
        "--threshold", "0", "--json", path, "--allow-tools", *SUITE_TOOLS], capture_output=True)
    if not os.path.exists(path):
        sys.exit(f"claude plugin eval wrote no report for {case} on {arm}; run it by hand to see why")
    return suite_results(json.load(open(path)), arm, built.text_hash(plugin), model, first)


def run_built_cases(cases, arm, plugin, model, judge, runs, out, first):
    if not cases:
        return []
    sub = os.path.join(out, f"built-{arm}-{first}")
    cmd = [sys.executable, os.path.join(EVALS, "_built", "run.py"), "--model", model, "--judge", judge,
           "--runs", str(runs), "--first", str(first), "--arm", f"{arm}={plugin}", "--out", sub]
    for c in cases:
        cmd += ["--case", c.split("/", 1)[1]]
    sh(cmd, cwd=EVALS, capture_output=True)
    results = json.load(open(os.path.join(sub, "results.json")))
    for r in results:
        r["case"] = f"_built/{r['case']}"
        r["cost"] = log_cost(os.path.join(sub, f"{r['case'].split('/', 1)[1]}-{arm}-{r['run']}.jsonl"))
    return results


def log_cost(log):
    cost = 0.0
    if os.path.exists(log):
        for line in open(log):
            if '"type":"result"' in line.replace(" ", ""):
                try:
                    cost += json.loads(line).get("total_cost_usd") or 0
                except ValueError:
                    pass
    return cost


def baseline_path(root, text, model, judge, case):
    return os.path.join(root, text, f"{model}--{judge}", case.replace("/", "__") + ".json")


def gate(records, as_guard):
    if not records:
        return ""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(records, f)
    cmd = [sys.executable, os.path.join(EVALS, "_built", "gate.py"), f.name] + (["--guard"] if as_guard else [])
    done = sh(cmd, capture_output=True)
    os.remove(f.name)
    return done.stdout + done.stderr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--judge", help="judge model for graded checks (the strongest model)")
    ap.add_argument("--model", action="append", help=f"agent model; default both of {', '.join(MODELS)}")
    ap.add_argument("--runs", type=int, default=6, help="runs per arm per model, counting runs already made")
    ap.add_argument("--baseline", default=os.path.join(EVALS, "results", "baseline"),
                    help="where main's runs are kept for reuse (a shared folder lets other work reuse them)")
    ap.add_argument("--out", default=os.path.join(EVALS, "results", "fast"))
    ap.add_argument("--full", action="store_true", help="select every case")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    models = a.model or MODELS

    failed = static()
    s = affected.select(affected.read_tree(a.base), affected.read_tree(), affected.load_cases(),
                        affected.routing_probes(), a.full)
    selected = s["decide"] + s["guard"]
    print(f"\ndecide {len(s['decide'])}, guard {len(s['guard'])}, routing {len(s['routing'])} ({s['routing_why']})")
    for c in selected:
        print(f"  {c:28} {s['why'][c]}")
    if s["full"]:
        print(f"full suite: {s['full_why']}: run every case (claude plugin eval and _built/run.py) instead")
        sys.exit(1 if failed else 0)
    with tempfile.TemporaryDirectory(prefix="fast-main-") as tmp:
        main_plugin = main_arm(a.base, os.path.join(tmp, "main"))
        texts = {"main": built.text_hash(main_plugin), "new": built.text_hash(PLUGIN)}
        # Runs made earlier for the same texts and case definitions count, so a later stage only tops them up.
        earlier = json.load(open(os.path.join(a.out, "results.json"))) \
            if os.path.exists(os.path.join(a.out, "results.json")) else []
        hashes = {c: case_hash(c) for c in selected}
        have = {}
        for r in earlier:
            if r["case"] in hashes and r.get("case_hash") == hashes[r["case"]] and r["text"] == texts[r["arm"]] \
                    and r.get("judge") == a.judge:
                have.setdefault((r["arm"], r["model"], r["case"]), []).append(r)
        for m in models:
            for c in selected:
                path = baseline_path(a.baseline, texts["main"], m, a.judge, c)
                if os.path.exists(path) and not have.get(("main", m, c)):
                    kept = json.load(open(path))
                    if kept["case_hash"] == hashes[c]:
                        have[("main", m, c)] = kept["records"]
        need = {(arm, m, c): max(0, a.runs - len(have.get((arm, m, c), [])))
                for arm in texts for m in models for c in selected}
        print(f"{sum(need.values())} case sessions to run ({sum(len(v) for v in have.values())} earlier runs "
              f"reused) and {len(s['routing']) * len(models)} routing sessions")
        if a.dry_run or not selected and not s["routing"]:
            sys.exit(1 if failed else 0)
        if failed:
            sys.exit("static checks failed; fix them before spending tokens on runs")
        if not a.judge:
            sys.exit("give --judge: graded checks need the strongest model as judge")
        records, spent = [r for v in have.values() for r in v], 0.0
        for model in models:
            out = os.path.join(a.out, model)
            os.makedirs(out, exist_ok=True)
            for arm, plugin in (("main", main_plugin), ("new", PLUGIN)):
                # Cases short by the same number of runs go to the runner together.
                by_need = {}
                for c in selected:
                    if need[(arm, model, c)]:
                        by_need.setdefault(need[(arm, model, c)], []).append(c)
                for n, cases in by_need.items():
                    first = a.runs - n + 1  # the same shortfall means the same runs made before
                    got = run_built_cases([c for c in cases if c.startswith("_built/")], arm, plugin, model, a.judge,
                                          n, out, first)
                    for c in cases:
                        if not c.startswith("_built/"):
                            got += run_suite_case(c, arm, plugin, model, a.judge, n, out, first)
                    for r in got:
                        r["case_hash"], r["judge"] = hashes[r["case"]], a.judge
                        spent += r.get("cost", 0)
                    records += got
                if arm == "main":
                    for c in selected:
                        path = baseline_path(a.baseline, texts["main"], model, a.judge, c)
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        with open(path, "w") as f:
                            json.dump({"case_hash": hashes[c], "records": [
                                r for r in records if r["case"] == c and r["arm"] == "main" and r["model"] == model]}, f)
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "results.json"), "w") as f:
            json.dump(records, f, indent=1)
        print(f"\nresults in {os.path.relpath(a.out, ROOT)}/results.json; the agent sessions this call ran cost "
              f"${spent:.2f}, judges not counted")
        print("deciding cases:\n" + gate([r for r in records if r["case"] in s["decide"]], False))
        print("guard cases:\n" + gate([r for r in records if r["case"] in s["guard"]], True))
        fell = []
        for model in models if s["routing"] else []:
            new_pass = routing(PLUGIN, model, s["routing"], os.path.join(a.out, "routing-new"))
            fails = [p for p, ok in new_pass.items() if not ok]
            if fails:
                on_main = routing(main_plugin, model, fails, os.path.join(a.out, "routing-main"))
                fell += [f"{p} on {model}" for p in fails if on_main.get(p)]
        if fell:
            print(f"routing fell (passes on main, fails on the change): {', '.join(fell)}")


def routing(plugin, model, probes, out):
    """{probe: passed} from _fast/routing.py, its report printed."""
    cmd = [sys.executable, os.path.join(HERE, "routing.py"), "--plugin", plugin, "--model", model, "--out", out]
    done = sh(cmd + [x for p in probes for x in ("--probe", p)], capture_output=True)
    print(done.stdout)
    return {line.split()[1]: line.startswith("PASS") for line in done.stdout.splitlines()
            if line.startswith(("PASS ", "FAIL "))}


if __name__ == "__main__":
    main()
