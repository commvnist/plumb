"""Works out plumb's next release from the commits since the last tag, and writes it into the files.

The bump comes from each commit's Conventional Commits subject: a `!` or a BREAKING CHANGE
footer is major, feat is minor, fix and perf are patch, anything else releases nothing. A
`release:major|minor|patch|none` label on the commit's pull request overrides its subject.
The largest bump across the commits wins. When the version in the files has no tag yet (it was
bumped by hand), that version is released as it is.

Writes the version into the plugin manifest and Codex files, turns the changelog's
"## Unreleased" section into the version's section (or lists the commit subjects when there is
none), writes that section to NOTES_PATH as the release notes, and prints the version.
Prints nothing and changes nothing when there is nothing to release.

Usage: python3 scripts/release.py NOTES_PATH   (needs `gh` signed in, to read pull request labels)
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MANIFEST = os.path.join(ROOT, "plumb", ".claude-plugin", "plugin.json")
CHANGELOG = os.path.join(ROOT, "plumb", "CHANGELOG.md")
SUBJECT = re.compile(r"^(\w+)(\([^)]*\))?(!)?: ")
BREAKING = re.compile(r"^BREAKING[ -]CHANGE: ", re.M)
TYPE_BUMPS = {"feat": "minor", "fix": "patch", "perf": "patch"}
ORDER = [None, "patch", "minor", "major"]


def bump_for(subject, body, labels):
    """The bump one commit asks for: major, minor, patch or None."""
    for label in labels:
        if label.startswith("release:"):
            bump = label.removeprefix("release:")
            if bump not in ORDER[1:] + ["none"]:
                sys.exit(f"unknown label {label!r}; use release:major, minor, patch or none")
            return None if bump == "none" else bump
    match = SUBJECT.match(subject)
    if not match:
        return None
    if match.group(3) or BREAKING.search(body):
        return "major"
    return TYPE_BUMPS.get(match.group(1))


def next_version(version, bump):
    major, minor, patch = (int(n) for n in version.split("."))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def section(text, heading):
    """The start and end of a "## heading" section's body, or None."""
    match = re.search(rf"^## {re.escape(heading)}\n", text, re.M)
    if not match:
        return None
    end = text.find("\n## ", match.end())
    return match.start(), match.end(), len(text) if end == -1 else end + 1


def changelog_for(text, version, subjects):
    """The changelog with a section for version, and that section's body as release notes."""
    found = section(text, version)
    if found:
        return text, text[found[1]:found[2]].strip() + "\n"
    found = section(text, "Unreleased")
    if found:
        start, body, end = found
        notes = text[body:end].strip() + "\n"
        return text[:start] + f"## {version}\n" + text[body:], notes
    notes = "".join(f"- {s}\n" for s in subjects)
    first = text.find("\n## ") + 1 or len(text)
    return text[:first] + f"## {version}\n\n{notes}\n" + text[first:], notes


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], check=True, capture_output=True, text=True).stdout


def pr_labels(sha):
    repo = os.environ["GITHUB_REPOSITORY"]
    out = subprocess.run(["gh", "api", f"repos/{repo}/commits/{sha}/pulls", "--jq", ".[].labels[].name"],
                         check=True, capture_output=True, text=True).stdout
    return out.split()


def main(notes_path):
    with open(MANIFEST) as f:
        manifest = json.load(f)
    current = manifest["version"]
    last_tag = git("describe", "--tags", "--abbrev=0", "--match", "v*").strip()
    log = git("log", "--format=%H%x00%s%x00%b%x1e", f"{last_tag}..HEAD")
    commits = [entry.strip("\n").split("\0") for entry in log.split("\x1e") if entry.strip()]
    bumps = [(subject, bump_for(subject, body, pr_labels(sha))) for sha, subject, body in commits]
    released = [subject for subject, bump in bumps if bump]

    if git("tag", "--list", f"v{current}").strip():
        bump = max((b for _, b in bumps), key=ORDER.index, default=None)
        if not bump:
            return
        version = next_version(current, bump)
    else:
        version = current

    manifest["version"] = version
    with open(MANIFEST, "w") as f:
        f.write(json.dumps(manifest, indent=2) + "\n")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_codex.py")], check=True,
                   stdout=subprocess.DEVNULL)
    with open(CHANGELOG) as f:
        text, notes = changelog_for(f.read(), version, released)
    with open(CHANGELOG, "w") as f:
        f.write(text)
    with open(notes_path, "w") as f:
        f.write(notes)
    print(version)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
