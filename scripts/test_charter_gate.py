"""Tests for plumb/hooks/charter-gate.sh. Run: python3 scripts/test_charter_gate.py"""

import json
import os
import subprocess
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..", "plumb")
HOOK = os.path.join(ROOT, "hooks", "charter-gate.sh")
HELD = "plumb held this call"


def charter_opening():
    with open(os.path.join(ROOT, "skills", "plumb", "SKILL.md")) as f:
        lines = f.read().split("# Plumb\n", 1)[1].splitlines()
    return next(line for line in lines if line.strip())


def entry(line):
    # A transcript line is a message, unless the test gives the whole entry (a compaction boundary).
    return line if isinstance(line, dict) and "type" in line else {"message": {"content": [line]}}


def run(tool, tool_input, transcript_lines, prefix=None, extra=None):
    with tempfile.NamedTemporaryFile("w", prefix=prefix, suffix=".jsonl", delete=False) as t:
        for line in transcript_lines:
            t.write(json.dumps(entry(line), separators=(",", ":")) + "\n")
    try:
        payload = {"hook_event_name": "PreToolUse", "transcript_path": t.name,
                   "tool_name": tool, "tool_input": tool_input, **(extra or {})}
        out = subprocess.run(["sh", HOOK], input=json.dumps(payload), capture_output=True,
                             text=True, check=True).stdout
    finally:
        os.unlink(t.name)
    return json.loads(out)["hookSpecificOutput"] if out else None


def held(tool, tool_input, transcript_lines):
    decision = run(tool, tool_input, transcript_lines)
    return bool(decision) and decision["permissionDecision"] == "deny" and HELD in decision["permissionDecisionReason"]


class CharterGate(unittest.TestCase):
    def test_holds_the_first_edit_or_commit_until_the_charter_is_loaded(self):
        loaded = ["Base directory for this skill: /p/skills/plumb\n\n# Plumb\n\n" + charter_opening()]
        cases = [
            # (tool, input, transcript, held)
            ("Edit", {"file_path": "a.py"}, ["fix the bug"], True),
            ("Write", {"file_path": "a.py"}, loaded, False),
            ("Bash", {"command": "git commit -m 'fix: x'"}, ["commit it"], True),
            ("Bash", {"command": "git -C repo push -u origin main"}, ["push it"], True),
            ("Bash", {"command": "cd repo\ngit commit -m 'fix: x'"}, ["commit it"], True),
            ("Bash", {"command": "git status && npm test"}, ["run tests"], False),
            ("Read", {"file_path": "a.py"}, ["read it"], False),
            ("Bash", {"command": "echo 'git commit'"}, ["say it"], False),
        ]
        for tool, tool_input, transcript, expected in cases:
            with self.subTest(tool=tool, tool_input=tool_input):
                self.assertEqual(held(tool, tool_input, transcript), expected)

    def test_holds_once_so_work_that_isnt_code_can_go_on(self):
        first = run("Write", {"file_path": "notes.md"}, ["write notes"])
        refusal = {"type": "tool_result", "is_error": True, "content": first["permissionDecisionReason"]}
        self.assertFalse(held("Write", {"file_path": "notes.md"}, ["write notes", refusal]))

    def test_holds_again_after_a_compaction_drops_the_charter(self):
        loaded = "Base directory for this skill: /p/skills/plumb\n\n# Plumb\n\n" + charter_opening()
        boundary = {"type": "system", "subtype": "compact_boundary", "content": "Conversation compacted"}
        summary = {"type": "user", "isCompactSummary": True, "message": {"content": "Loaded " + charter_opening()}}
        self.assertTrue(held("Edit", {"file_path": "a.py"}, [loaded, boundary, summary, "go on"]))
        self.assertFalse(held("Edit", {"file_path": "a.py"}, [boundary, "go on", loaded]))
        first = run("Edit", {"file_path": "a.py"}, [loaded, boundary])
        refusal = {"type": "tool_result", "is_error": True, "content": first["permissionDecisionReason"]}
        self.assertFalse(held("Edit", {"file_path": "a.py"}, [loaded, boundary, refusal]))

    def test_reads_a_subagents_own_transcript(self):
        # A subagent's call carries the session's transcript path and the agent's id.
        loaded = "Base directory for this skill: /p/skills/plumb\n\n# Plumb\n\n" + charter_opening()
        with tempfile.TemporaryDirectory() as d:
            session = os.path.join(d, "s1.jsonl")
            with open(session, "w") as f:
                f.write(json.dumps(entry(loaded)) + "\n")
            os.makedirs(os.path.join(d, "s1", "subagents"))
            agent = os.path.join(d, "s1", "subagents", "agent-a1b2.jsonl")

            def call():
                payload = {"hook_event_name": "PreToolUse", "transcript_path": session, "agent_id": "a1b2",
                           "tool_name": "Write", "tool_input": {"file_path": "notes.md"}}
                out = subprocess.run(["sh", HOOK], input=json.dumps(payload), capture_output=True,
                                     text=True, check=True).stdout
                return json.loads(out)["hookSpecificOutput"] if out else None

            with open(agent, "w") as f:
                f.write(json.dumps(entry("write the notes")) + "\n")
            first = call()
            self.assertTrue(first and HELD in first["permissionDecisionReason"])
            with open(agent, "a") as f:
                f.write(json.dumps(entry({"type": "tool_result", "content": first["permissionDecisionReason"]})) + "\n")
            self.assertIsNone(call())

    def test_reads_a_transcript_path_that_json_escapes(self):
        # A Windows path's backslashes arrive escaped in the hook's JSON input.
        decision = run("Edit", {"file_path": "a.py"}, ["fix the bug"], prefix="C:\\Users\\dev\\")
        self.assertTrue(decision and HELD in decision["permissionDecisionReason"])

    def test_lets_the_call_through_without_a_transcript(self):
        # Copilot CLI gives no transcript here, and a failing hook would refuse the call.
        payload = {"tool_name": "Edit", "tool_input": {"file_path": "a.py"}}
        result = subprocess.run(["sh", HOOK], input=json.dumps(payload), capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_charter_opening_reads_the_same_inside_json(self):
        # The hook finds the charter by this line in the JSON transcript, unescaped.
        opening = charter_opening()
        self.assertEqual(json.dumps(opening)[1:-1], opening)


if __name__ == "__main__":
    unittest.main()
