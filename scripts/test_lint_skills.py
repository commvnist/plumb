"""Tests for scripts/lint_skills.py's checks on texts given in place of the plugin's.

Usage: python3 scripts/test_lint_skills.py
"""
import importlib.util
import os
import unittest

_spec = importlib.util.spec_from_file_location(
    "lint_skills", os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint_skills.py"))
lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint)


def skill(name, description, body="Body."):
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n"


class Checks(unittest.TestCase):
    def errors(self, found):
        return lint.check(found)[0]

    def test_clean_texts_pass(self):
        self.assertEqual(self.errors({"skills/plumb-a/SKILL.md": skill("plumb-a", 'Use for "x". See plumb-b.'),
                                      "skills/plumb-b/SKILL.md": skill("plumb-b", 'Use for "y".')}), [])

    def test_name_that_points_nowhere(self):
        errors = self.errors({"skills/plumb-a/SKILL.md": skill("plumb-a", "A.", "Load plumb-gone first.")})
        self.assertTrue(any("plumb-gone" in e for e in errors), errors)

    def test_trigger_phrase_in_two_descriptions(self):
        errors = self.errors({"skills/plumb-a/SKILL.md": skill("plumb-a", 'Use for "Review this".'),
                              "skills/plumb-b/SKILL.md": skill("plumb-b", 'Use for "review this".')})
        self.assertTrue(any("trigger phrase 'review this'" in e for e in errors), errors)

    def test_frontmatter_name_differs_from_folder(self):
        errors = self.errors({"skills/plumb-a/SKILL.md": skill("plumb-b", "A.")})
        self.assertTrue(any("frontmatter name" in e for e in errors), errors)

    def test_description_over_the_limit(self):
        errors = self.errors({"skills/plumb-a/SKILL.md": skill("plumb-a", "x" * 1025)})
        self.assertTrue(any("1025 characters" in e for e in errors), errors)

    def test_agent_block_description_is_read(self):
        agent = "---\nname: plumb-r\ndescription: |\n  Reviews.\ntools: []\n---\n\nBody.\n"
        self.assertEqual(self.errors({"agents/plumb-r.md": agent}), [])

    def test_repeat_shared_by_two_files(self):
        line = "one two three four five six seven eight nine"
        shared = lint.repeats({"skills/plumb-a/SKILL.md": skill("plumb-a", "A.", line),
                               "skills/plumb-b/SKILL.md": skill("plumb-b", "B.", "and " + line)})
        self.assertEqual(list(shared), [line])


if __name__ == "__main__":
    unittest.main()
