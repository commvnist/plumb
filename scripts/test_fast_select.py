"""Tests for plumb/evals/_fast/affected.py, the case selection the fast eval tier runs.

The replays are the regressions earlier gates caught by running many more cases: each applies the wording that
lowered a check to today's text and asserts that the selection holds the case where the check fell. A selection
that drops one of them would have let that regression land.

Usage: python3 scripts/test_fast_select.py
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
_spec = importlib.util.spec_from_file_location("affected", os.path.join(ROOT, "plumb", "evals", "_fast", "affected.py"))
affected = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(affected)

# The replays edit the text as it stood when they were written, so a later rewording of a replayed phrase
# leaves them standing; the selection rules and cases are today's.
PINNED = "47181db"
MAIN = affected.read_tree(PINNED)
assert MAIN, f"commit {PINNED} is not in this clone: fetch the full history (actions/checkout with fetch-depth: 0)"
CASES = affected.load_cases()
PROBES = affected.routing_probes()


def selection(*edits):
    """The selection for the pinned text with each (file, old, new) edit applied; old must occur once."""
    new = dict(MAIN)
    for name, old, text in edits:
        assert new[name].count(old) == 1, f"{old!r} occurs {new[name].count(old)} times in {name}"
        new[name] = new[name].replace(old, text)
    return affected.select(MAIN, new, CASES, PROBES)


def picked(s):
    return set(s["feature"]) | set(s["decide"]) | set(s["hold"]) | set(s["guard"])


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
        self.assertIn("bf-medium-auto", s["hold"])
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
        self.assertIn("bf-large-reuse", s["hold"])
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

    def test_removed_guarded_phrase_must_hold(self):
        s = selection(("plumb-debug", " an intermittent one by forcing its cause", ""))
        self.assertIn("bf-small-flaky", s["hold"])


class ChangeType(unittest.TestCase):
    """The gate fits the change: a rewording holds, an addition to covered text beats main, new text is judged
    by a case written for it, and new text with no case is owed one."""

    def test_addition_to_covered_text_decides(self):
        s = selection(("plumb-debug", "1. **Reproduce** the exact error;", "1. **Reproduce** the exact error, "
                       "from the reporter's own steps;"))
        self.assertIn("bf-small-flaky", s["decide"])
        self.assertEqual(s["owed"], [])

    def test_new_text_with_its_own_case_is_a_feature(self):
        step = "8. **Record it** where the team tracks defects."
        new = dict(MAIN, **{"plumb-debug": MAIN["plumb-debug"].rstrip("\n") + "\n" + step + "\n"})
        cases = dict(CASES, **{"_built/record": {"kind": "built", "loads": {"plumb-debug"}, "tags": [],
                                                  "guards": [("plumb-debug", "where the team tracks defects")]}})
        s = affected.select(MAIN, new, cases, PROBES, old_cases=set(CASES))
        self.assertEqual(s["feature"], ["_built/record"])
        self.assertEqual(s["owed"], [])
        self.assertIn("bf-small-flaky", s["guard"])

    def test_reworded_phrase_with_its_guard_updated_holds(self):
        # check_refs makes a rewording of a guarded phrase update its guard; the case is still main's to hold.
        old_phrase, new_phrase = "an intermittent one by forcing its cause", "an intermittent one by provoking its cause"
        new = dict(MAIN, **{"plumb-debug": MAIN["plumb-debug"].replace(old_phrase, new_phrase)})
        cases = {k: dict(v, guards=[(f, new_phrase if p == old_phrase else p) for f, p in v["guards"]])
                 for k, v in CASES.items()}
        s = affected.select(MAIN, new, cases, PROBES, old_cases=set(CASES))
        self.assertIn("bf-small-flaky", s["hold"])
        self.assertEqual(s["feature"], [])

    def test_shorter_rewording_of_an_opening_holds(self):
        s = selection(("plumb-review", "- **Verdict:** approve | approve with suggestions | request changes,",
                       "- **Verdict:** approve, approve with suggestions or request changes,"))
        self.assertIn("_built/review-scope", s["hold"])
        self.assertEqual(s["decide"] + s["owed"], [])

    def test_new_text_without_a_case_is_owed_one(self):
        step = "8. **Record it** where the team tracks defects."
        new = dict(MAIN, **{"plumb-debug": MAIN["plumb-debug"].rstrip("\n") + "\n" + step + "\n"})
        s = affected.select(MAIN, new, CASES, PROBES)
        self.assertEqual(s["owed"], ["plumb-debug Steps 8"])
        self.assertEqual(s["feature"] + s["decide"], [])

    def test_section_reference_links_every_unit_under_it(self):
        text = "---\nname: plumb-a\n---\n\nUse plumb-b's \"Output\" here.\n"
        b = "---\nname: plumb-b\n---\n\n## Output\n\n- **Done:** a\n- **Waiting on:** b\n"
        old = {"plumb-a": text, "plumb-b": b}
        cases = {"c": {"kind": "suite", "loads": set(), "tags": [], "guards": [("plumb-a", "Use plumb-b")]}}
        s = affected.select(old, dict(old, **{"plumb-b": b.replace("** b", "** c")}), cases)
        self.assertEqual(s["guard"], ["c"])

    def test_every_built_case_says_what_it_loads(self):
        self.assertTrue(all(c["loads"] for c in CASES.values() if c["kind"] == "built"))


class CaseHash(unittest.TestCase):
    def test_same_in_two_processes(self):
        # Runs are reused only when the hash matches the one recorded with them, in an earlier process.
        code = ("import importlib.util as u; s = u.spec_from_file_location('r', 'plumb/evals/_fast/run.py'); "
                "m = u.module_from_spec(s); s.loader.exec_module(m); "
                "print(m.case_hash('_built/review-voice'), m.case_hash('bf-small-flaky'))")
        runs = [subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
                .stdout for _ in range(2)]
        self.assertEqual(runs[0], runs[1])

    def test_changes_with_what_a_built_case_reads(self):
        # A built case's prompt can live in the suite table; a run on the old prompt must not be reused.
        run = importlib.util.module_from_spec(importlib.util.spec_from_file_location(
            "fast_run", os.path.join(ROOT, "plumb", "evals", "_fast", "run.py")))
        run.__spec__.loader.exec_module(run)
        before = run.case_hash("_built/carrier")
        with tempfile.TemporaryDirectory() as tmp:
            copy = os.path.join(tmp, "evals")
            shutil.copytree(run.EVALS, copy, ignore=shutil.ignore_patterns("results", "__pycache__"))
            with open(os.path.join(copy, "_fixtures", "write_cases.py"), "a") as f:
                f.write("\n# edited\n")
            run.EVALS = copy
            self.assertNotEqual(run.case_hash("_built/carrier"), before)


class FeatureBar(unittest.TestCase):
    """A feature's case passes in at least two thirds of runs on each model, from six runs."""

    def verdict(self, **runs):
        run = importlib.util.module_from_spec(importlib.util.spec_from_file_location(
            "fast_run_bar", os.path.join(ROOT, "plumb", "evals", "_fast", "run.py")))
        run.__spec__.loader.exec_module(run)
        records = [{"case": "c", "arm": "new", "model": m, "checks": {"x": ok}}
                   for m, oks in runs.items() for ok in oks]
        return run.accept(records, ["h", "s"])

    def test_two_thirds_on_each_model_passes(self):
        self.assertIn("does what it promises", self.verdict(h=[True] * 4 + [False] * 2, s=[True] * 6))

    def test_one_model_short_of_two_thirds_fails(self):
        self.assertIn("falls short", self.verdict(h=[True] * 3 + [False] * 3, s=[True] * 6))

    def test_too_few_runs_asks_for_more(self):
        self.assertIn("run each model to 6", self.verdict(h=[True] * 3, s=[True] * 6))

    def test_a_model_with_no_measured_runs_is_short(self):
        self.assertIn("run each model to 6", self.verdict(s=[True] * 6))


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
