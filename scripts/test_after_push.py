"""Tests for plumb/hooks/after-push.sh. Run: python3 scripts/test_after_push.py"""

import json
import os
import subprocess
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "plumb", "hooks", "after-push.sh")
REMINDER = "charter rule 20"


def run(command, transcript_lines=(), output=" * [new branch]      HEAD -> main", copilot=False, transcript=True):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as t:
        for line in transcript_lines:
            t.write(json.dumps(line, separators=(",", ":")) + "\n")
    try:
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
        if output is not None:
            payload["tool_response"] = {"stdout": output}
        if transcript:
            payload["transcript_path"] = t.name
        env = {k: v for k, v in os.environ.items() if k != "COPILOT_PLUGIN_ROOT"}
        if copilot:
            env["COPILOT_PLUGIN_ROOT"] = "/plugin"
        return subprocess.run(["sh", HOOK], input=json.dumps(payload), capture_output=True,
                              text=True, check=True, env=env).stdout
    finally:
        os.unlink(t.name)


def said(out):
    return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else ""


class AfterPush(unittest.TestCase):
    def test_reminds_after_work_leaves_and_not_otherwise(self):
        cases = [
            ("git push -u origin fix/tax", " * [new branch]      fix/tax -> fix/tax", True),
            ("cd svc && git -C . push", "Everything up-to-date", True),
            ("git push", "fatal: expected 'acknowledgments', received 'packfile'\n"
                         "warning: push negotiation failed; proceeding anyway with push\n"
                         " * [new branch]      HEAD -> main", True),
            ('gh pr create --title "fix: tax" --body "Rounds tax."', "https://github.com/o/r/pull/4", True),
            ("git push origin main", " ! [rejected]        main -> main (fetch first)\n"
                                     "error: failed to push some refs", False),
            ("git push", "fatal: could not read Username", False),
            ("git status", "", False),
            ("git commit -m 'docs: explain git push'", "", False),
            ("gh pr view 4", "", False),
        ]
        for command, output, reminded in cases:
            with self.subTest(command=command):
                self.assertEqual(REMINDER in said(run(command, output=output)), reminded)

    def test_said_once_until_a_compaction(self):
        first = said(run("git push"))
        self.assertIn(REMINDER, first)
        before = [{"message": {"content": [first]}}]
        self.assertEqual(run("git push", before), "")
        boundary = {"type": "system", "subtype": "compact_boundary"}
        self.assertIn(REMINDER, said(run("git push", before + [boundary])))

    def test_says_nothing_without_a_transcript(self):
        # Without one there is no way to say it only once, and a reminder on every push is noise.
        self.assertEqual(run("git push", transcript=False), "")

    def test_a_tool_that_reports_no_output_is_reminded(self):
        self.assertIn(REMINDER, said(run("git push", output=None)))

    def test_answers_in_the_shape_each_tool_reads(self):
        self.assertIn(REMINDER, json.loads(run("git push", copilot=True))["additionalContext"])


if __name__ == "__main__":
    unittest.main()
