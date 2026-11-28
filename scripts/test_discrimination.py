"""Tests for plumb/evals/_fast/discrimination.py. Run: python3 scripts/test_discrimination.py"""
import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "discrimination", os.path.join(os.path.dirname(__file__), "..", "plumb", "evals", "_fast", "discrimination.py"))
discrimination = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discrimination)


def run_file(arms):
    """A with-without run of one case whose graders pass as `arms` says: {arm: [{grader: passed}]}."""
    graders = [{"name": "judged", "type": "llm"}, {"name": "no-edit", "type": "tool_used", "config": {"max": 0}},
               {"name": "skill-x", "type": "tool_used", "config": {"min": 1}}]
    case = {"name": "c", "graders": graders, "arms": {
        arm: [{"graders": [{"name": n, "passed": p, "scored": n != "skill-x"} for n, p in run.items()]}
              for run in runs] for arm, runs in arms.items()}}
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"cases": [case]}, f)
    f.close()
    return f.name


def listed(arms):
    path = run_file(arms)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            discrimination.main([path])
    finally:
        os.unlink(path)
    return out.getvalue()


class Discrimination(unittest.TestCase):
    def test_lists_a_grader_no_plumb_passes_as_often(self):
        out = listed({"with": [{"judged": True, "no-edit": True, "skill-x": True}] * 2,
                      "without": [{"judged": True, "no-edit": True, "skill-x": False}] * 2})
        self.assertIn("both pass", out)
        self.assertIn("judged", out)
        self.assertNotIn("no-edit", out)  # a limit both arms keep isn't a fault
        self.assertNotIn("skill-x", out)  # an unscored indicator isn't judged

    def test_keeps_quiet_about_a_grader_plumb_moves(self):
        out = listed({"with": [{"judged": True, "no-edit": True}] * 2,
                      "without": [{"judged": False, "no-edit": True}, {"judged": True, "no-edit": True}]})
        self.assertIn("every grader passes more often with plumb", out)

    def test_names_a_grader_both_arms_fail(self):
        out = listed({"with": [{"judged": False}], "without": [{"judged": False}]})
        self.assertIn("both fail", out)


if __name__ == "__main__":
    unittest.main()
