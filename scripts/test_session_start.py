"""Tests for plumb/hooks/session-start.sh. Run: python3 scripts/test_session_start.py"""

import json
import os
import subprocess
import unittest

HOOKS = os.path.join(os.path.dirname(__file__), "..", "plumb", "hooks")


def run(copilot):
    env = {k: v for k, v in os.environ.items() if k != "COPILOT_PLUGIN_ROOT"}
    if copilot:
        env["COPILOT_PLUGIN_ROOT"] = "/plugin"
    return subprocess.run(["sh", os.path.join(HOOKS, "session-start.sh")], capture_output=True,
                          text=True, check=True, env=env).stdout


class SessionStart(unittest.TestCase):
    def test_gives_the_reminder_in_the_shape_each_tool_reads(self):
        # Claude Code and Codex take plain output as context; Copilot CLI takes only JSON.
        with open(os.path.join(HOOKS, "session-start.md")) as f:
            reminder = f.read().strip()
        self.assertEqual(run(copilot=False).strip(), reminder)
        self.assertEqual(json.loads(run(copilot=True))["additionalContext"], reminder)


if __name__ == "__main__":
    unittest.main()
