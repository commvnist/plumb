"""Tests for the gh stand-in in plumb/evals/_built/sim.py. Run: python3 scripts/test_sim.py"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plumb", "evals", "_built"))
import sim  # noqa: E402

GIT = {"GIT_AUTHOR_NAME": "Dev", "GIT_AUTHOR_EMAIL": "dev@example.com",
       "GIT_COMMITTER_NAME": "Dev", "GIT_COMMITTER_EMAIL": "dev@example.com"}


class PullRequests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "repo")
        self.env = {**os.environ, **GIT, **sim.install(os.path.join(self.tmp.name, "sim"), ("gh",))}
        self.sh("git init -q -b main . && git commit -q --allow-empty -m init")

    def tearDown(self):
        self.tmp.cleanup()

    def sh(self, cmd):
        os.makedirs(self.repo, exist_ok=True)
        return subprocess.run(["bash", "-c", cmd], cwd=self.repo, env=self.env, capture_output=True, text=True,
                              check=True).stdout

    def view(self, n=""):
        return json.loads(self.sh(f"gh pr view {n} --json title,body,headRefName,files"))

    def test_serves_a_pull_request_the_session_opened_as_last_sent(self):
        self.sh("git checkout -qb feat/x && echo a > a && git add a && git commit -qm 'feat: a'")
        self.sh("gh pr create --title 'feat: a' --body 'Reads RETRIES.'")
        self.assertEqual(self.view()["body"], "Reads RETRIES.")
        self.sh("printf 'Reads MAX_ATTEMPTS.' > b.md && gh pr edit --body-file b.md")
        got = self.view()
        self.assertEqual((got["title"], got["body"], got["headRefName"]), ("feat: a", "Reads MAX_ATTEMPTS.", "feat/x"))
        self.assertEqual(got["files"], [{"path": "a"}])

    def test_a_filled_create_takes_the_head_commit(self):
        self.sh("git checkout -qb feat/y && echo y > y && git add y && git commit -qm 'feat: y' -m 'Why y.'")
        self.sh("gh pr create --fill")
        got = self.view()
        self.assertEqual((got["title"], got["body"]), ("feat: y", "Why y."))

    def test_an_edit_to_the_scaffolds_pull_request_keeps_what_it_didnt_send(self):
        self.sh("git checkout -qb pr-12 && echo f > f && git add f && git commit -qm 'fix: x' -m 'Body of the fix.' "
                "&& git checkout -q main")
        self.sh("gh pr edit 12 --add-label ready")
        got = self.view(12)
        self.assertEqual((got["title"], got["body"], got["headRefName"]), ("fix: x", "Body of the fix.", "pr-12"))
        self.assertEqual(got["files"], [{"path": "f"}])
        self.sh("gh pr edit 12 --body updated")
        self.assertEqual((self.view(12)["title"], self.view(12)["body"]), ("fix: x", "updated"))


if __name__ == "__main__":
    unittest.main()
