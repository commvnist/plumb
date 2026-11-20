"""Tests for scripts/release.py. Run: python3 scripts/test_release.py"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from release import bump_for, changelog_for, next_version  # noqa: E402

CHANGELOG = """# Changelog

Intro.

## Unreleased

### Added
- A thing.

## 0.6.0

Old.
"""


class Bump(unittest.TestCase):
    def test_bump_from_commit_and_labels(self):
        cases = [
            # (subject, body, labels, bump)
            ("feat: add a thing", "", [], "minor"),
            ("feat(build): add a thing", "", [], "minor"),
            ("fix: stop a crash", "", [], "patch"),
            ("perf: load less text", "", [], "patch"),
            ("feat!: drop the old hook", "", [], "major"),
            ("fix(hooks)!: rename the hook", "", [], "major"),
            ("feat: new report", "Body.\n\nBREAKING CHANGE: the report line moved", [], "major"),
            ("docs: reword the README", "", [], None),
            ("ci: cache pip", "", [], None),
            ("chore(release): 0.6.0", "", [], None),
            ("Merge pull request #8 from x/y", "", [], None),
            ("[SHOP-42] feat(pricing): add tax", "", [], "minor"),
            ("[SHOP-42] fix!: drop the old hook", "", [], "major"),
            ("[WIP] feat: half done", "", [], None),
            ("fix: small", "", ["release:minor"], "minor"),
            ("feat!: big", "", ["release:patch"], "patch"),
            ("docs: notes", "", ["release:major", "docs"], "major"),
            ("feat: internal only", "", ["release:none"], None),
        ]
        for subject, body, labels, bump in cases:
            with self.subTest(subject=subject, labels=labels):
                self.assertEqual(bump_for(subject, body, labels), bump)

    def test_shipped_text_releases_at_least_a_patch(self):
        cases = [
            # (subject, labels, files, bump)
            ("refactor: trim the test skill", [], ["plumb/skills/plumb-test/SKILL.md"], "patch"),
            ("docs: reword a hook note", [], ["plumb/hooks/user-prompt.md"], "patch"),
            ("chore: tidy an agent", [], ["plumb/agents/plumb-scout.md"], "patch"),
            ("docs: reword the README", [], ["README.md", "plumb/README.md"], None),
            ("test(evals): add a case", [], ["plumb/evals/bf-x/case.yaml"], None),
            ("refactor: trim the test skill", ["release:none"], ["plumb/skills/plumb-test/SKILL.md"], None),
            ("feat: add a skill", [], ["plumb/skills/plumb-x/SKILL.md"], "minor"),
        ]
        for subject, labels, files, bump in cases:
            with self.subTest(subject=subject, labels=labels):
                self.assertEqual(bump_for(subject, "", labels, files), bump)

    def test_next_version(self):
        self.assertEqual(next_version("0.6.0", "patch"), "0.6.1")
        self.assertEqual(next_version("0.6.3", "minor"), "0.7.0")
        self.assertEqual(next_version("0.6.3", "major"), "1.0.0")


class Changelog(unittest.TestCase):
    def test_unreleased_section_becomes_the_version(self):
        text, notes = changelog_for(CHANGELOG, "0.7.0", ["feat: x"])
        self.assertIn("## 0.7.0\n\n### Added\n- A thing.\n\n## 0.6.0", text)
        self.assertNotIn("Unreleased", text)
        self.assertEqual(notes, "### Added\n- A thing.\n")

    def test_existing_version_section_is_released_as_written(self):
        text, notes = changelog_for(CHANGELOG, "0.6.0", ["feat: x"])
        self.assertEqual(text, CHANGELOG)
        self.assertEqual(notes, "Old.\n")

    def test_without_an_entry_the_commit_subjects_are_listed(self):
        plain = CHANGELOG.replace("## Unreleased\n\n### Added\n- A thing.\n\n", "")
        text, notes = changelog_for(plain, "0.6.1", ["fix: stop a crash", "perf: load less"])
        self.assertIn("Intro.\n\n## 0.6.1\n\n- fix: stop a crash\n- perf: load less\n\n## 0.6.0", text)
        self.assertEqual(notes, "- fix: stop a crash\n- perf: load less\n")


if __name__ == "__main__":
    unittest.main()
