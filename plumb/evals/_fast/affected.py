"""Picks the eval cases a change to plumb's text needs, so a gate runs those instead of the whole suite.

  python3 _fast/affected.py [--base origin/main] [--json]

Run from plumb/evals. It compares the plugin's text (skills, agents, hook texts, README) at --base with the
working tree, splits each file into units (a numbered rule or step, a list item, a paragraph, the frontmatter)
and reports, for every unit that changed:

- decide: cases that guard a phrase inside a changed unit (_fixtures/guards.json, _built/guards.json). They are
  the evidence for that text, so they decide the change by the rules in plumb/evals/README.md.
- guard: cases that guard a unit the changed one points at, or that points at it ("charter rule 19", "plumb-plan
  step 4", plumb-x's "Section"), and, outside the charter, every case that loads the changed skill or dispatches
  the changed agent. A change is read where it is used: the regressions past gates caught sat in these cases as
  often as in the deciding ones (see scripts/test_fast_select.py).
- routing: the probes in _fast/routing.py that expect or forbid a skill whose description changed; all of them
  when a skill is added or removed, or a hook text changes, since either can move any request.
- full: the whole suite, only when the selection would cover most of it anyway or --full is given.

Static checks (scripts/lint_skills.py, scripts/check_refs.py and the case checks) cost no tokens and always run.
The charter is loaded in every case, so a change there selects by its units only, never by loading.
"""
import argparse
import difflib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.dirname(HERE)
PLUGIN = os.path.dirname(EVALS)
ROOT = os.path.dirname(PLUGIN)
NUMBERED = re.compile(r"^(\d+)\. \*\*")
ITEM = re.compile(r"^(\d+\. |- )")
# A selection this large saves little over the whole suite and misses what the rest would have shown.
FULL_SHARE = 0.6
AGENTS = {name[:-3] for name in os.listdir(os.path.join(PLUGIN, "agents"))}


def text_files():
    """{name: path relative to the plugin} for every text the agent reads, named as check_refs.py names them."""
    files = {}
    for name in sorted(os.listdir(os.path.join(PLUGIN, "skills"))):
        files[name] = f"skills/{name}/SKILL.md"
    for name in sorted(os.listdir(os.path.join(PLUGIN, "agents"))):
        files[name[:-3]] = f"agents/{name}"
    files["README"] = "README.md"
    for name in ("session-start", "user-prompt"):
        files[name] = f"hooks/{name}.md"
    return files


def units(text):
    """Splits a text into units: [(label, first line, last line)], lines counted from 0.

    The frontmatter is one unit; under a heading, each numbered or bulleted item is one (with its indented or
    wrapped lines), and so is each other paragraph."""
    lines = text.splitlines()
    found, section, i = [], "", 0
    if lines and lines[0] == "---":
        end = next((j for j in range(1, len(lines)) if lines[j] == "---"), len(lines) - 1)
        found.append(("frontmatter", 0, end))
        i = end + 1
    start = None

    def close(j):
        nonlocal start
        if start is not None:
            head = lines[start]
            m = NUMBERED.match(head)
            label = f"{section} {m.group(1)}" if m else f"{section}: {' '.join(head.split()[:6])}"
            found.append((label.strip(), start, j))
            start = None

    for j in range(i, len(lines)):
        line = lines[j]
        if line.startswith("#"):
            close(j - 1)
            section = line.lstrip("#").strip()
            found.append((f"heading {section}", j, j))
        elif not line.strip():
            close(j - 1)
        elif ITEM.match(line):
            close(j - 1)
            start = j
        elif start is None:
            start = j
    close(len(lines) - 1)
    return found


def unit_of(spans, lineno):
    return next((u for u in spans if u[1] <= lineno <= u[2]), None)


def changed_units(old, new):
    """Labels of the units a change touched, from both sides of a line diff."""
    old_lines, new_lines = old.splitlines(), new.splitlines()
    old_spans, new_spans = units(old), units(new)
    touched = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        # An insertion between units touches the unit it lands in, or the one just before it.
        for spans, a, b in ((old_spans, i1, i2), (new_spans, j1, j2)):
            for n in range(a, max(b, a + 1)):
                u = unit_of(spans, n) or unit_of(spans, n - 1)
                if u and not u[0].startswith("heading"):
                    touched.add(u[0])
    return touched


def rule_numbers(fragment):
    """Charter rule numbers a unit points at: every number after its first "charter rule" (or, in the charter,
    "rule"), ranges like "16 to 18" or "16–18" expanded."""
    out = set()
    for n1, n2 in re.findall(r"\b(\d+)(?:\s*(?:to|[–-])\s*(\d+))?\b", fragment):
        out.update(range(int(n1), int(n2 or n1) + 1))
    return out


def references(name, text):
    """{unit label: set of (file name, unit label)} for the numbered and section references in each unit."""
    refs = {}
    for label, a, b in units(text):
        body = "\n".join(text.splitlines()[a:b + 1])
        targets = set()
        m = re.search(r"\b[Rr]ules? \d" if name == "plumb" else r"charter rules? \d", body)
        if m:
            targets |= {("plumb", f"Rules {n}") for n in rule_numbers(body[m.start():])}
        for skill, first, last in re.findall(r"(plumb(?:-[a-z]+)?)(?:'s)? steps? (\d+)(?:[–-](\d+))?", body):
            targets |= {(skill, f"Steps {n}") for n in range(int(first), int(last or first) + 1)}
        own = re.sub(r"plumb(?:-[a-z]+)?(?:'s)? steps? \d+(?:[–-]\d+)?", "", body)
        for first, last in re.findall(r"\b[Ss]teps? (\d+)(?:[–-](\d+))?", own):
            targets |= {(name, f"Steps {n}") for n in range(int(first), int(last or first) + 1)}
        for skill, section in re.findall(r"(plumb(?:-[a-z]+)?)'s \"([^\"]+)\"", body):
            targets.add((skill, ("section", section)))
        refs[label] = targets
    return refs


def load_cases():
    """Every case: {name: {"loads": set of skill and agent names, "guards": [(file, phrase)], "kind": ...}}."""
    sys.path.insert(0, os.path.join(EVALS, "_fixtures"))
    from write_cases import CASES  # noqa: E402
    cases = {}
    for name, case in CASES.items():
        loads = set()
        for g in case["graders"].values():
            if g.get("type") == "tool_used" and g.get("tool") in ("Skill", "Agent") and g.get("input_match"):
                loads |= set(re.findall(r"(plumb(?:-[a-z]+)?)\"", g["input_match"]))
        cases[name] = {"kind": "suite", "loads": loads, "tags": case["tags"], "guards": []}
    for name, entries in json.load(open(os.path.join(EVALS, "_fixtures", "guards.json"))).items():
        cases[name]["guards"] = [tuple(e[:2]) for e in entries]
    spec = importlib.util.spec_from_file_location("built_run", os.path.join(EVALS, "_built", "run.py"))
    built = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(built)
    built_guards = json.load(open(os.path.join(EVALS, "_built", "guards.json")))
    for name, case in built.BUILT.items():
        cases[f"_built/{name}"] = {"kind": "built", "loads": set(built.LOADS[name]), "tags": [],
                                   "guards": [tuple(e[:2]) for e in built_guards.get(name, [])]}
    return cases


def git_show(rev, path):
    done = subprocess.run(["git", "show", f"{rev}:plumb/{path}"], cwd=ROOT, capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else None


def read_tree(rev=None):
    texts = {}
    for name, path in text_files().items():
        if rev:
            texts[name] = git_show(rev, path)
        elif os.path.exists(os.path.join(PLUGIN, path)):
            texts[name] = open(os.path.join(PLUGIN, path)).read()
    # A skill or agent the other side lacks is still compared, as added or removed.
    if rev:
        for kind in ("skills", "agents"):
            listing = subprocess.run(["git", "ls-tree", "--name-only", f"{rev}:plumb/{kind}"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.split()
            for entry in listing:
                name = entry if kind == "skills" else entry[:-3]
                path = f"skills/{entry}/SKILL.md" if kind == "skills" else f"agents/{entry}"
                texts.setdefault(name, git_show(rev, path))
    return {k: v for k, v in texts.items() if v is not None}


def locate(text, phrase):
    """Labels of the units holding a phrase (a phrase may span lines inside one unit)."""
    found = set()
    for label, a, b in units(text):
        if phrase in "\n".join(text.splitlines()[a:b + 1]):
            found.add(label)
    return found


def select(old, new, cases, routing_probes=(), full=False):
    """The selection for a change from texts `old` to texts `new` ({file name: text})."""
    names = sorted(set(old) | set(new))
    changed = {n: changed_units(old.get(n, ""), new.get(n, "")) for n in names if old.get(n) != new.get(n)}
    added = sorted(n for n in changed if n not in old)
    removed = sorted(n for n in changed if n not in new)
    reasons = {}  # case -> (tier, reason)
    agents = {n for n in names if n in AGENTS}

    def dispatchers(agent):
        """The skills other than the charter whose text names the agent."""
        return {n for n in names if n not in agents and n != "plumb" and n.startswith("plumb")
                and agent in (new.get(n) or old.get(n) or "")}

    def pick(case, tier, why):
        if case not in reasons or (tier == "decide" and reasons[case][0] != "decide"):
            reasons[case] = (tier, why)

    # Units the change points at, or that point at it, by number or section name.
    linked = set()
    for side in (old, new):
        for n, text in side.items():
            for label, targets in references(n, text).items():
                for f, target in targets:
                    # A section named by its heading stands for every unit under it.
                    if isinstance(target, tuple):
                        sec = target[1]
                        each = [l for l, _, _ in units(side.get(f, "")) if l.startswith((f"{sec} ", f"{sec}:"))]
                    else:
                        each = [target]
                    for t in each:
                        if label in changed.get(n, ()):
                            linked.add((f, t))
                        if t in changed.get(f, ()):
                            linked.add((n, label))

    for case, info in cases.items():
        for f, phrase in info["guards"]:
            if f not in changed and not any(n == f for n, _ in linked):
                continue
            here = locate(old.get(f, ""), phrase) | locate(new.get(f, ""), phrase)
            hit = here & changed.get(f, set())
            if hit or (phrase in old.get(f, "") and phrase not in new.get(f, "")):
                pick(case, "decide", f"guards {phrase!r} in {f} ({', '.join(sorted(hit)) or 'removed'})")
            elif any((f, u) in linked for u in here):
                via = sorted(u for u in here if (f, u) in linked)
                pick(case, "guard", f"guards {f} {', '.join(via)}, which the change points at or which points at it")
        for f in changed:
            if f != "plumb" and f in info["loads"]:
                pick(case, "guard", f"loads {f}")
            # An agent's text is read wherever a skill that dispatches it is loaded.
            elif f in agents:
                via = sorted(info["loads"] & dispatchers(f))
                if via:
                    pick(case, "guard", f"loads {via[0]}, which dispatches {f}")

    routing = []
    described = {n for n in changed if "frontmatter" in changed[n]}
    if added or removed or {"session-start", "user-prompt"} & set(changed):
        routing = [p for p, _ in routing_probes]
        routing_why = "a skill was added or removed, or a hook text changed: any request can route differently"
    elif described:
        routing = [p for p, skills in routing_probes if skills & {n.replace("plumb-", "") for n in described}
                   or ("charter" in skills and "plumb" in described)]
        routing_why = f"description changed: {', '.join(sorted(described))}"
    else:
        routing_why = "no description changed"

    share = len(reasons) / max(len(cases), 1)
    run_full = full or share >= FULL_SHARE
    return {
        "changed": {n: sorted(u) for n, u in changed.items()},
        "added": added, "removed": removed,
        "decide": sorted(c for c, (t, _) in reasons.items() if t == "decide"),
        "guard": sorted(c for c, (t, _) in reasons.items() if t == "guard"),
        "why": {c: w for c, (_, w) in sorted(reasons.items())},
        "routing": routing, "routing_why": routing_why,
        "full": run_full,
        "full_why": ("asked for" if full else
                     f"the selection covers {share:.0%} of the suite" if run_full else ""),
    }


def routing_probes():
    """[(probe id, the skills it expects or forbids)] from _fast/routing.py."""
    spec = importlib.util.spec_from_file_location("routing", os.path.join(HERE, "routing.py"))
    routing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(routing)
    return [(pid, set(p[3]) | set(p[4])) for pid, p in routing.PROBES.items()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="origin/main", help="the revision the change is compared with")
    ap.add_argument("--full", action="store_true", help="select the whole suite")
    ap.add_argument("--json", action="store_true", help="print the selection as JSON for _fast/run.py")
    a = ap.parse_args()
    s = select(read_tree(a.base), read_tree(), load_cases(), routing_probes(), a.full)
    if a.json:
        print(json.dumps(s, indent=1))
        return
    if not s["changed"]:
        print(f"no plugin text differs from {a.base}: static checks only")
        return
    print("changed units:")
    for n, us in s["changed"].items():
        print(f"  {n}: {'; '.join(us) or '(whole file)'}")
    for tier in ("decide", "guard"):
        print(f"{tier} ({len(s[tier])}):")
        for c in s[tier]:
            print(f"  {c:28} {s['why'][c]}")
    print(f"routing ({len(s['routing'])}): {s['routing_why']}")
    if s["full"]:
        print(f"full suite: {s['full_why']}")


if __name__ == "__main__":
    main()
