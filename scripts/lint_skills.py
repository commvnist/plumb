"""Static checks on plumb's skill, agent and hook texts: the part of the eval gate that costs no tokens.

- Frontmatter: each skill and agent names itself as its folder or file does, and has a description of at most
  1,024 characters (the longest a host is required to read).
- Names: every plumb-x the texts mention is a skill or an agent, so a pointer can't send the agent nowhere.
- Routing: no quoted trigger phrase ("review this") sits in two skills' descriptions, since a request matching
  it would have two skills claiming it.
- Size: the words in each file, and in the text every session loads (the descriptions and hook texts), are pinned
  in scripts/lint.lock, so growth is seen in review: every word is loaded wherever its file is.
- Repeats: runs of eight or more words shared by two files are pinned too, so a rule restated in a second place is
  seen in review (CONTRIBUTING.md: say it once).

A changed size or a new repeat fails until the lock is rewritten with --update, as scripts/refs.lock works.

Usage: python3 scripts/lint_skills.py [--update]
"""
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PLUGIN = os.path.join(ROOT, "plumb")
LOCK = os.path.join(ROOT, "scripts", "lint.lock")
REPEAT = 8
DESCRIPTION_MAX = 1024


def texts():
    """{path relative to the plugin: text} for every text the agent reads."""
    found = {}
    for name in sorted(os.listdir(os.path.join(PLUGIN, "skills"))):
        found[f"skills/{name}/SKILL.md"] = None
    for name in sorted(os.listdir(os.path.join(PLUGIN, "agents"))):
        found[f"agents/{name}"] = None
    for name in ("session-start", "user-prompt"):
        found[f"hooks/{name}.md"] = None
    return {p: open(os.path.join(PLUGIN, p)).read() for p in found}


def frontmatter(text):
    """({key: value}, body). A `key: |` block takes its indented lines as the value."""
    if not text.startswith("---\n"):
        return {}, text
    head, _, body = text[4:].partition("\n---\n")
    fields, key = {}, None
    for line in head.splitlines():
        m = re.match(r"^([\w-]+):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2)
            fields[key] = "" if value == "|" else value
        elif key and line.startswith("  "):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields, body


def words(text):
    return re.findall(r"[\w'’`*<>-]+", text.lower())


def check(found):
    errors, sizes, always = [], {}, 0
    known = {p.split("/")[1] for p in found if p.startswith("skills/")} | \
            {p.split("/")[1][:-3] for p in found if p.startswith("agents/")}
    triggers = {}
    for path, text in found.items():
        fields, body = frontmatter(text)
        own = path.split("/")[1] if path.startswith("skills/") else path.split("/")[1][:-3]
        if not path.startswith("hooks/"):
            if fields.get("name") != own:
                errors.append(f"{path}: frontmatter name is {fields.get('name')!r}, expected {own!r}")
            description = fields.get("description", "")
            if not description:
                errors.append(f"{path}: no description in its frontmatter")
            elif len(description) > DESCRIPTION_MAX:
                errors.append(f"{path}: description is {len(description)} characters, over {DESCRIPTION_MAX}")
            always += len(words(description))
            if path.startswith("skills/"):
                for phrase in re.findall(r'"([^"]+)"', description):
                    triggers.setdefault(phrase.lower(), []).append(own)
        else:
            always += len(words(text))
        for lineno, line in enumerate(text.splitlines(), 1):
            for name in re.findall(r"\bplumb-[a-z]+", line):
                if name not in known:
                    errors.append(f"{path}:{lineno}: names {name}, which is no skill or agent")
        sizes[path] = len(words(body)) + (len(words(fields.get("description", ""))))
    for phrase, owners in sorted(triggers.items()):
        if len(owners) > 1:
            errors.append(f"trigger phrase {phrase!r} is in the descriptions of {', '.join(owners)}")
    sizes["always loaded"] = always
    return errors, sizes, repeats(found)


def repeats(found):
    """Runs of REPEAT words shared by two or more files, merged into their longest spans: {text: [paths]}."""
    seen = {}
    for path, text in found.items():
        fields, body = frontmatter(text)
        w = words(fields.get("description", "") + " " + body)
        for i in range(len(w) - REPEAT + 1):
            seen.setdefault(tuple(w[i:i + REPEAT]), set()).add(path)
    shared = {g: paths for g, paths in seen.items() if len(paths) > 1}
    spans = {}
    for path, text in found.items():
        fields, body = frontmatter(text)
        w = words(fields.get("description", "") + " " + body)
        i = 0
        while i <= len(w) - REPEAT:
            g = tuple(w[i:i + REPEAT])
            if g in shared:
                j = i
                while j + REPEAT < len(w) and tuple(w[j + 1:j + 1 + REPEAT]) in shared:
                    j += 1
                spans.setdefault(" ".join(w[i:j + REPEAT]), set()).update(
                    *(shared[tuple(w[k:k + REPEAT])] for k in range(i, j + 1)))
                i = j + REPEAT
            else:
                i += 1
    return {s: sorted(paths) for s, paths in sorted(spans.items())}


def main(update):
    errors, sizes, shared = check(texts())
    current = {"words": sizes, "repeats": shared}
    if update:
        with open(LOCK, "w") as f:
            json.dump(current, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"updated {os.path.relpath(LOCK, ROOT)}")
    else:
        pinned = json.load(open(LOCK)) if os.path.exists(LOCK) else {"words": {}, "repeats": {}}
        for path in sorted(set(sizes) | set(pinned["words"])):
            was, now = pinned["words"].get(path), sizes.get(path)
            if was != now:
                errors.append(f"{path}: {was} words pinned, {now} now: if the change earns them, run with --update")
        for span in sorted(set(shared) - set(pinned["repeats"])):
            errors.append(f"repeated in {', '.join(shared[span])}: {span!r}: say it once, or pin it with --update")
        for span in sorted(set(pinned["repeats"]) - set(shared)):
            errors.append(f"scripts/lint.lock pins a repeat that is gone: {span!r}: run with --update")
    for e in errors:
        print(e)
    if errors:
        sys.exit(1)
    print(f"skills ok ({sizes['always loaded']} words loaded in every session)")


if __name__ == "__main__":
    main("--update" in sys.argv)
