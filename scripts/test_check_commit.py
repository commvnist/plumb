"""Tests for plumb/hooks/check-commit.sh. Run: python3 scripts/test_check_commit.py"""

import json
import os
import subprocess
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "plumb", "hooks", "check-commit.sh")
GIT = ["git", "-c", "user.email=dev@example.com", "-c", "user.name=Dev", "-c", "commit.gpgsign=false"]


def git(repo, *args):
    subprocess.run(GIT + ["-C", repo, *args], check=True, capture_output=True)


def run_hook(repo, command, output=""):
    payload = {"hook_event_name": "PostToolUse", "cwd": repo, "tool_name": "Bash",
               "tool_input": {"command": command}, "tool_response": {"stdout": output}}
    out = subprocess.run(["sh", HOOK], input=json.dumps(payload), capture_output=True,
                         text=True, check=True).stdout
    return "isn't Conventional Commits" in out


class CheckCommit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-q")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "chore: start")

    def tearDown(self):
        self.tmp.cleanup()

    def test_flags_only_a_fresh_non_conventional_commit(self):
        cases = [
            # (subject, command run, flagged)
            ("Add total with tax", "git commit -m 'Add total with tax'", True),
            ("feat: add total with tax", "git commit -m 'feat: add total with tax'", False),
            ("feat(pricing)!: drop float prices", "git commit -m x", False),
            ("Update stuff", "git status", False),
            ("Update stuff", 'git -C "$repo" commit -m "$(cat <<EOF\nUpdate stuff\nEOF\n)"', True),
            ("Update stuff", "npm run commitlint", False),
        ]
        for subject, command, flagged in cases:
            with self.subTest(subject=subject, command=command):
                git(self.repo, "commit", "-q", "--allow-empty", "-m", subject)
                self.assertEqual(run_hook(self.repo, command), flagged)

    def test_ignores_a_commit_only_mentioned_in_the_output(self):
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "Made by the user")
        self.assertFalse(run_hook(self.repo, "git status", "no changes added to commit"))

    def test_ignores_an_old_commit_when_this_command_made_none(self):
        old = {**os.environ, "GIT_COMMITTER_DATE": "2000-01-01T00:00:00"}
        subprocess.run(GIT + ["-C", self.repo, "commit", "-q", "--allow-empty", "-m", "Old"],
                       check=True, env=old)
        self.assertFalse(run_hook(self.repo, "git commit -m 'nothing to commit'"))

    def test_ignores_a_merge_commit(self):
        git(self.repo, "checkout", "-q", "-b", "side")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "feat: side")
        git(self.repo, "checkout", "-q", "-")
        git(self.repo, "merge", "-q", "--no-ff", "--no-commit", "side")
        git(self.repo, "commit", "-q", "--no-edit")
        self.assertFalse(run_hook(self.repo, "git commit --no-edit"))


if __name__ == "__main__":
    unittest.main()
