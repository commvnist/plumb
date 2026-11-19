"""Checks that every numbered cross-reference in plumb's skills still points at the right target.

References checked:
  charter rule N / rule N (in the charter) / Rules N–M    -> a numbered charter rule
  plumb-x step N, or step(s) N[–M] inside plumb-x          -> a numbered step in that skill's Steps
  plumb-x's "Section"                                      -> a heading in that skill

A number that exists can still point at the wrong thing after an insert or a renumber, so the
title of every numbered rule and step is pinned in scripts/refs.lock. When a title at a number
changes, the check fails until you have re-read every reference to it and run with --update.

Each eval case names the skill text it is evidence for (plumb/evals/_fixtures/guards.json, written by
write_cases.py), optionally with the grader that measures it. When that text is gone, the check fails
until the case is changed or removed with it.

Every numbered rule and step that no case guards is listed in scripts/unguarded.txt, so a new line
without a case is seen in review: the check fails until the list matches, which --update rewrites.
An unguarded line is owed a case, not first to cut.

Usage: python3 scripts/check_refs.py [--update]
"""
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PLUGIN = os.path.join(ROOT, "plumb")
LOCK = os.path.join(ROOT, "scripts", "refs.lock")
GUARDS = os.path.join(PLUGIN, "evals", "_fixtures", "guards.json")
UNGUARDED = os.path.join(ROOT, "scripts", "unguarded.txt")
NUMBERED = re.compile(r"^(\d+)\. \*\*(.+?)\*\*")
DASH = r"[–-]"


def skill_files():
    files = {}
    skills = os.path.join(PLUGIN, "skills")
    for name in sorted(os.listdir(skills)):
        files[name] = os.path.join(skills, name, "SKILL.md")
    agents = os.path.join(PLUGIN, "agents")
    for name in sorted(os.listdir(agents)):
        files[name[:-3]] = os.path.join(agents, name)
    files["README"] = os.path.join(PLUGIN, "README.md")
    # Hook text reaches the agent as context, so a case can guard it too.
    for name in ("session-start", "user-prompt"):
        files[name] = os.path.join(PLUGIN, "hooks", name + ".md")
    return files


def numbered(text, section):
    """Numbered bold items under the '## <section>' heading."""
    items, inside = {}, False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip() == section
            continue
        m = NUMBERED.match(line)
        if inside and m:
            items[int(m.group(1))] = m.group(2).rstrip(".:,")
    return items


def headings(text):
    return {line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")}


def numbers(first, last):
    return range(int(first), int(last or first) + 1)


def main(update):
    files = skill_files()
    texts = {name: open(path).read() for name, path in files.items()}
    rules = numbered(texts["plumb"], "Rules")
    steps = {name: numbered(text, "Steps") for name, text in texts.items()}
    errors = []

    for name, text in texts.items():
        for lineno, line in enumerate(text.splitlines(), 1):
            where = f"{os.path.relpath(files[name], ROOT)}:{lineno}"
            # Inside the charter a bare "rule N" means a charter rule; elsewhere it must say "charter rule N".
            prefix = r"\b[Rr]ules? " if name == "plumb" else r"charter rules? "
            rule_pattern = rf"{prefix}(\d+)(?:{DASH}(\d+))?"
            for m in re.finditer(rule_pattern, line):
                for n in numbers(m.group(1), m.group(2)):
                    if n not in rules:
                        errors.append(f"{where}: charter rule {n} does not exist")
            for m in re.finditer(rf"(plumb(?:-[a-z]+)?)(?:'s)? steps? (\d+)(?:{DASH}(\d+))?", line):
                target = m.group(1)
                for n in numbers(m.group(2), m.group(3)):
                    if n not in steps.get(target, {}):
                        errors.append(f"{where}: {target} step {n} does not exist")
            own = re.sub(r"plumb(?:-[a-z]+)?(?:'s)? steps? \d+(?:[–-]\d+)?", "", line)
            for m in re.finditer(rf"\b[Ss]teps? (\d+)(?:{DASH}(\d+))?", own):
                for n in numbers(m.group(1), m.group(2)):
                    if n not in steps.get(name, {}):
                        errors.append(f"{where}: step {n} does not exist in {name}")
            for m in re.finditer(r"(plumb(?:-[a-z]+)?)'s \"([^\"]+)\"", line):
                if m.group(2) not in headings(texts.get(m.group(1), "")):
                    errors.append(f"{where}: {m.group(1)} has no section \"{m.group(2)}\"")

    guards = json.load(open(GUARDS))
    for case, entries in guards.items():
        for name, phrase, *_ in entries:
            if phrase not in texts.get(name, ""):
                errors.append(f"evals/{case} guards {phrase!r} in {name}, which is no longer there: "
                              "change or remove the case with the text")

    unguarded = []
    for name, items in [("plumb", rules)] + sorted(steps.items()):
        for n, title in sorted(items.items()):
            line = next(l for l in texts[name].splitlines() if NUMBERED.match(l) and l.startswith(f"{n}. "))
            if not any(e[0] == name and e[1] in line for entries in guards.values() for e in entries):
                unguarded.append(f"{name} {n}: {title}")

    current = {"charter rules": {str(k): v for k, v in rules.items()},
               "steps": {name: {str(k): v for k, v in s.items()} for name, s in steps.items() if s}}
    if update:
        with open(LOCK, "w") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
            f.write("\n")
        with open(UNGUARDED, "w") as f:
            f.write("".join(u + "\n" for u in unguarded))
        print(f"updated {os.path.relpath(LOCK, ROOT)} and {os.path.relpath(UNGUARDED, ROOT)}")
    else:
        listed = open(UNGUARDED).read().splitlines() if os.path.exists(UNGUARDED) else []
        for u in sorted(set(unguarded) - set(listed)):
            errors.append(f"{u} has no eval case guarding it: add one, or run with --update to list it as owed")
        for u in sorted(set(listed) - set(unguarded)):
            errors.append(f"scripts/unguarded.txt lists {u!r}, which is now guarded or gone: run with --update")
        pinned = json.load(open(LOCK)) if os.path.exists(LOCK) else {}
        if pinned != current:
            errors.append("a numbered rule or step changed its title or number since scripts/refs.lock: "
                          "re-read every reference to it, then run with --update")

    for e in errors:
        print(e)
    if errors:
        sys.exit(1)
    print("references ok")


if __name__ == "__main__":
    main("--update" in sys.argv)
