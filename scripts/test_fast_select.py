"""Tests for plumb/evals/_fast/affected.py, the case selection the fast eval tier runs.

The replays are the regressions earlier gates caught by running many more cases: each applies the wording that
lowered a check to today's text and asserts that the selection holds the case where the check fell. A selection
that drops one of them would have let that regression land.

Usage: python3 scripts/test_fast_select.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
_spec = importlib.util.spec_from_file_location("affected", os.path.join(ROOT, "plumb", "evals", "_fast", "affected.py"))
affected = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(affected)

MAIN = affected.read_tree()
CASES = affected.load_cases()
PROBES = affected.routing_probes()


def selection(*edits):
    """The selection for today's text with each (file, old, new) edit applied; old must occur once."""
    new = dict(MAIN)
    for name, old, text in edits:
        assert new[name].count(old) == 1, f"{old!r} occurs {new[name].count(old)} times in {name}"
        new[name] = new[name].replace(old, text)
    return affected.select(MAIN, new, CASES, PROBES)


def picked(s):
    return set(s["decide"]) | set(s["guard"])


class Replays(unittest.TestCase):
    """Each wording below lowered a check in a past gate; the case that showed it must be selected."""

    def test_review_voice_rewording(self):
        # Consistency pass, 2026-11-26: review-voice Haiku 6/6 -> 2/4.
        s = selection(("plumb-review", "in charter rule 19's voice", "in the operator's voice (charter rule 19)"))
        self.assertIn("_built/review-voice", picked(s))

    def test_review_comment_blocking_label(self):
        # Critical rounds, 2026-11-26: "each comment says whether it blocks" was read as a label to print.
        s = selection(("plumb-review", "each finding sits at its line, unnumbered,",
                       "each finding sits at its line, unnumbered, says whether it blocks,"))
        self.assertIn("_built/review-voice", picked(s))

    def test_auto_review_reason_cut(self):
        # Consistency pass, 2026-11-26: bf-medium-auto Sonnet reviewer 11/18 -> 4/18.
        s = selection(("plumb-auto", ", since an author can't see past their own assumptions", ""),
                      ("plumb-auto", ", and leaves a record they can check every choice against", ""))
        self.assertIn("bf-medium-auto", s["decide"])
        self.assertIn("bf-small-route-away", picked(s))
        self.assertIn("auto-away", s["routing"])

    def test_auditor_brief_trim(self):
        # Consistency pass, 2026-11-26: bf-large-audit-all Haiku one-suite-run 18/18 -> 14/18.
        s = selection(("plumb-auditor", " (and `plumb-test` for tests)", ""),
                      ("plumb-auditor", ", what you didn't reach included", ""))
        self.assertIn("bf-large-audit-all", picked(s))

    def test_ship_corrected_description(self):
        # Critical rounds, 2026-11-26: "offer the corrected text" for a description later commits make untrue,
        # pr-rename Sonnet 4/5 -> 1/5.
        s = selection(("plumb-ship", "and where to look first.",
                       "and where to look first; when later commits make a description untrue, offer the corrected "
                       "text."))
        self.assertIn("_built/pr-rename", picked(s))

    def test_debug_reach(self):
        # Eval harness recovery, 2026-11-23: red every run (flaky-commit) Haiku 5/6 -> 0/6, p 0.008.
        s = selection(("plumb-debug", "3. **Name the cause** a run confirmed, in one sentence;",
                       "3. **Name the cause** a run confirmed, in one sentence, and its reach: since when, and what "
                       "it already wrote or sent;"))
        self.assertIn("_built/flaky-commit", picked(s))


class Selection(unittest.TestCase):
    def test_no_change_selects_nothing(self):
        s = affected.select(MAIN, MAIN, CASES, PROBES)
        self.assertEqual((s["decide"], s["guard"], s["routing"], s["full"]), ([], [], [], False))

    def test_charter_rule_selects_its_cases_not_every_case(self):
        s = selection(("plumb", "5. **Take the first rung that works:**", "5. **Take the lowest rung that works:**"))
        self.assertIn("bf-large-reuse", s["decide"])
        self.assertLess(len(picked(s)), len(CASES) / 4)
        self.assertEqual(s["routing"], [])

    def test_reference_to_a_changed_rule_selects_its_users(self):
        # plumb-build step 5 points at charter rule 16; a case guarding step 5 must come with a change to rule 16.
        s = selection(("plumb", "16. **A test earns its place** by catching a realistic break;",
                       "16. **A test earns its place** by catching a break that could happen;"))
        self.assertIn("bf-small-build-ship", picked(s))

    def test_new_skill_runs_every_routing_probe(self):
        new = dict(MAIN, **{"plumb-jira": "---\nname: plumb-jira\ndescription: Jira.\n---\n\n# Plumb: jira\n"})
        s = affected.select(MAIN, new, CASES, PROBES)
        self.assertEqual(s["added"], ["plumb-jira"])
        self.assertEqual(len(s["routing"]), len(PROBES))

    def test_removed_guarded_phrase_decides(self):
        s = selection(("plumb-debug", " an intermittent one by forcing its cause", ""))
        self.assertIn("bf-small-flaky", s["decide"])

    def test_section_reference_links_every_unit_under_it(self):
        text = "---\nname: plumb-a\n---\n\nUse plumb-b's \"Output\" here.\n"
        b = "---\nname: plumb-b\n---\n\n## Output\n\n- **Done:** a\n- **Waiting on:** b\n"
        old = {"plumb-a": text, "plumb-b": b}
        cases = {"c": {"kind": "suite", "loads": set(), "tags": [], "guards": [("plumb-a", "Use plumb-b")]}}
        s = affected.select(old, dict(old, **{"plumb-b": b.replace("** b", "** c")}), cases)
        self.assertEqual(s["guard"], ["c"])

    def test_every_built_case_says_what_it_loads(self):
        self.assertTrue(all(c["loads"] for c in CASES.values() if c["kind"] == "built"))


class Units(unittest.TestCase):
    TEXT = "---\nname: x\n---\n\n# X\n\n## Steps\n\n1. **One** a\n   wrapped\n2. **Two** b\n\nA paragraph.\n"

    def test_numbered_items_and_paragraphs(self):
        labels = [u[0] for u in affected.units(self.TEXT)]
        self.assertEqual(labels, ["frontmatter", "heading X", "heading Steps", "Steps 1", "Steps 2",
                                  "Steps: A paragraph."])

    def test_edit_on_a_wrapped_line_touches_its_item(self):
        self.assertEqual(affected.changed_units(self.TEXT, self.TEXT.replace("wrapped", "wrapped more")),
                         {"Steps 1"})


if __name__ == "__main__":
    unittest.main()
