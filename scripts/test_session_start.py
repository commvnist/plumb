"""Tests for plumb/hooks/session-start.sh. Run: python3 scripts/test_session_start.py"""

import json
import os
import subprocess
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..", "plumb")
HOOKS = os.path.join(ROOT, "hooks")


def run(copilot, source="startup"):
    env = {k: v for k, v in os.environ.items() if k != "COPILOT_PLUGIN_ROOT"}
    if copilot:
        env["COPILOT_PLUGIN_ROOT"] = "/plugin"
    payload = json.dumps({"hook_event_name": "SessionStart", "source": source})
    return subprocess.run(["sh", os.path.join(HOOKS, "session-start.sh")], input=payload, capture_output=True,
                          text=True, check=True, env=env).stdout


def expected_reminder():
    with open(os.path.join(HOOKS, "session-start.md")) as f:
        reminder = f.read().strip()
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as f:
        version = json.load(f)["version"]
    return reminder.replace("The plumb plugin is installed.", f"The plumb plugin {version} is installed.", 1)


class SessionStart(unittest.TestCase):
    def test_gives_the_reminder_and_version_in_the_shape_each_tool_reads(self):
        # Claude Code and Codex take plain output as context; Copilot CLI takes only JSON.
        reminder = expected_reminder()
        self.assertNotEqual(reminder, open(os.path.join(HOOKS, "session-start.md")).read().strip())
        self.assertEqual(run(copilot=False).strip(), reminder)
        self.assertEqual(json.loads(run(copilot=True))["additionalContext"], reminder)

    def test_asks_to_reload_the_skills_after_a_compaction(self):
        for copilot in (False, True):
            with self.subTest(copilot=copilot):
                out = run(copilot, source="compact")
                text = json.loads(out)["additionalContext"] if copilot else out
                self.assertTrue(text.strip().startswith(expected_reminder()))
                self.assertIn("compacted", text)
                self.assertNotIn("compacted", run(copilot, source="resume"))


if __name__ == "__main__":
    unittest.main()
