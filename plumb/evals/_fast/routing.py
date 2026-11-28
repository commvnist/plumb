"""Routing probes: short requests whose wording sits between skills, each with the plumb skills that must load
and those that must not. A session runs three turns with writes and agents disabled, so a probe costs cents.

  python3 _fast/routing.py --plugin <plugin dir> --model <agent model> [--probe <id> ...] [--runs 1] [--out DIR]

Run from plumb/evals, once per agent model. A probe passes when every run loads each expected skill and none of
the forbidden ones; the exit status is 1 when any probe fails. A probe that fails on a change is run on main as
well before it counts against the change, since some wordings route unevenly on main too.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.dirname(HERE)
GIT_ENV = {"GIT_AUTHOR_NAME": "Dev", "GIT_AUTHOR_EMAIL": "dev@example.com",
           "GIT_COMMITTER_NAME": "Dev", "GIT_COMMITTER_EMAIL": "dev@example.com"}

# id: (fixture, setup, prompt, expect, forbid); skill names without the "plumb-" prefix, the charter as "charter".
S, O = "shop-small", "orders-medium"
DIRTY_S = "printf '\\n\\ndef cents(amount):\\n    return int(amount * 100)\\n' >> shop/pricing.py"
PROBES = {
 "build-euro": (S, "", "Add a format_euro function to shop/pricing.py that formats an amount like 1.234,50 €.", ["build"], ["plan","auto","debug"]),
 "build-inclusive": (S, "", "Make the coupon minimum in cart.py inclusive, so a subtotal exactly at the minimum gets the coupon.", ["build"], ["plan","auto","debug","refactor"]),
 "build-flag": (O, "", "Add an optional `limit` query parameter to the list-invoices handler.", ["build"], ["plan","auto"]),
 "debug-crash": (S, "", "Customers who type a price like 1,200.50 get a crash from parse_price. Fix it.", ["debug"], ["build","auto"]),
 "debug-flaky": (S, "", "test_cart fails maybe one run in ten on CI and passes locally. What's going on?", ["debug"], ["test","explain"]),
 "debug-why": (O, "", "Why does a customer with the loyalty discount sometimes get charged the full price?", ["debug"], ["explain","build"]),
 "test-add": (S, "", "Add tests for shop/cart.py.", ["test"], ["debug","audit","auto"]),
 "test-judge": (S, "", "Is tests/test_pricing.py a good test file? Tell me what you'd change.", ["test"], ["build","debug"]),
 "test-regression": (S, "", "Add a regression test for the coupon minimum boundary.", ["test"], ["debug","auto"]),
 "test-e2e": (O, "", "Add an end-to-end test that places an order and then fetches its invoice.", ["test"], ["auto"]),
 "refactor-clean": (S, "", "shop/pricing.py has gotten messy. Clean it up without changing what it does.", ["refactor"], ["build","audit"]),
 "refactor-rename": (S, "", "Rename Cart.item_count to Cart.quantity everywhere.", ["refactor"], ["plan","debug"]),
 "refactor-simplify": (O, "", "Simplify app/discounts.py.", ["refactor"], ["build"]),
 "review-commit": (O, "", "Review my last commit.", ["review"], ["audit","build"]),
 "review-merge": (O, "git checkout -qb feat/x && sed -i 's/return/return  /' app/discounts.py && git commit -qam 'feat: tweak'", "Look over this branch before I merge it into master.", ["review"], ["audit","ship"]),
 "audit-debt": (O, "", "Where's the tech debt in this service? What should we fix first?", ["audit"], ["review","refactor"]),
 "audit-prune": (S, "", "Which of our tests are pulling their weight and which can go?", ["audit"], ["refactor"]),
 "audit-security": (O, "", "Check the auth module for security holes.", ["audit"], ["build","debug"]),
 "plan-currency": (S, "", "How should we add multi-currency support? Don't write code yet.", ["plan"], ["build","auto"]),
 "plan-column": (O, "", "Rename the orders.total column to total_cents.", ["plan"], ["auto"]),
 "plan-big": (O, "", "We need refunds: partial and full, with the invoice and shipping updated. Break it down for me.", ["plan"], ["build","auto","jira"]),
 "explain-coupon": (S, "", "Walk me through how a coupon gets applied to a cart.", ["explain"], ["build","debug","review"]),
 "explain-why": (S, "", "Why does pricing use Decimal instead of float?", ["explain"], ["build","refactor"]),
 "explain-ownership": (O, "", "How do the ownership checks work in this service?", ["explain"], ["audit","review"]),
 "ship-commit": (S, DIRTY_S, "Commit this.", ["ship"], ["build","review","jira"]),
 "ship-notes": (O, "", "Write release notes for the last three commits.", ["ship"], ["review","explain","jira"]),
 "ship-pr": (S, "git checkout -qb feat/cents && " + DIRTY_S + " && git commit -qam 'feat: add cents'", "Write the PR description for this branch.", ["ship"], ["review","jira"]),
 "auto-away": (S, "", "Add a format_euro function to shop/pricing.py with tests. I'm heading out for the day, so just get it done without checking in.", ["auto"], ["plan"]),
 "auto-oneshot": (O, "", "One-shot this: add a handler that lets a customer cancel an order that hasn't shipped.", ["auto"], []),
 "auto-not-e2e": (S, "", "Fix the crash in parse_price for inputs like 1,200.50 end to end, including tests.", ["debug"], ["auto"]),
 "none-question": (S, "", "What's the difference between Decimal's ROUND_HALF_UP and ROUND_HALF_EVEN?", [], ["build","debug","refactor","plan","auto","test"]),
 "none-git": (S, "", "How many commits are in this repo?", [], ["build","debug","refactor","plan","auto","ship","audit","review"]),
}
PROBES.update({
 "build-spaces": (S, "", "Can you make parse_price accept prices with spaces in them, like '1 200.50'?", ["build"], ["debug","auto"]),
 "debug-wrong": (S, "", "Cart total comes out a cent off for three items at 3.33 with 10% tax. That's wrong.", ["debug"], ["build","explain"]),
 "debug-redtest": (S, "sed -i 's/assert /assert not /' tests/test_pricing.py", "tests/test_pricing.py is failing, sort it out.", ["debug"], ["test","build"]),
 "refactor-tidy": (S, "", "Get rid of duplicated rounding logic in shop/pricing.py.", ["refactor"], ["build","audit"]),
 "review-check": (S, DIRTY_S, "Check my work before I commit it.", ["review"], ["ship","audit"]),
 "review-safe": (O, "git checkout -qb fix/y && printf '\\n# ok\\n' >> app/auth.py && git commit -qam 'fix: auth'", "Is this branch safe to merge?", ["review"], ["audit"]),
 "explain-onboard": (O, "", "I'm new here. Help me understand how this service is laid out before I change anything.", ["explain"], ["audit","build","plan"]),
 "plan-doc": (O, "", "Draft a design for adding webhooks when an order ships.", ["plan"], ["build","auto","jira"]),
 "ship-bump": (S, "", "Bump the version to 1.2.0.", ["ship"], ["build"]),
 "auto-trust": (O, "", "Take it from here and finish it yourself: add an endpoint that exports a customer's orders as CSV.", ["auto"], ["plan"]),
 "auto-e2e-feature": (S, "", "Build a split_bill(amount, people) helper end to end, tests included.", ["build"], ["auto"]),
 "jira-bug": (S, "", "File a bug for the parse_price crash on prices like 1,200.50.", ["jira"], ["build","ship","debug"]),
 "jira-issue": (S, "", "Open a GitHub issue asking for multi-currency support.", ["jira"], ["plan","build"]),
 "jira-update": (S, "", "Post an update on PROJ-42 saying the coupon minimum fix is merged.", ["jira"], ["ship"]),
 "jira-comment": (S, "", "Comment on SHOP-57 that the fix is up for review at https://github.example/acme/shop/pull/12.", ["jira"], ["build","review"]),
 "jira-move": (S, "", "Move SHOP-57 to Done.", ["jira"], ["build","ship"]),
 "jira-epic": (O, "", "Create a Jira epic for refunds with a story each for partial and full refunds.", ["jira"], ["build","auto"]),
 "pr-update": (S, "", "Post an update on PR 12 saying Sam's review comment is addressed.", ["jira"], ["build","review"]),
})


def fired(log):
    """The skills a session loaded, as the probe table names them, and its cost in dollars."""
    names, cost = [], 0.0
    with open(log) as f:
        for line in f:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if record.get("type") == "assistant":
                for part in record["message"]["content"]:
                    if part.get("type") == "tool_use" and part.get("name") == "Skill":
                        skill = part["input"].get("skill", "").split(":")[-1]
                        names.append("charter" if skill == "plumb" else skill.replace("plumb-", ""))
            elif record.get("type") == "result":
                cost += record.get("total_cost_usd") or 0
    return names, cost


def run_one(pid, n, plugin, model, out):
    fixture, setup, prompt, _, _ = PROBES[pid]
    log = os.path.join(out, f"{pid}.{n}.jsonl")
    with tempfile.TemporaryDirectory(prefix=f"route-{pid}-") as tmp:
        repo = os.path.join(tmp, "repo")
        subprocess.run([sys.executable, os.path.join(EVALS, "_fixtures", "make.py"), fixture, repo], check=True,
                       capture_output=True)
        if setup:
            subprocess.run(["bash", "-c", setup], cwd=repo, check=True, env={**os.environ, **GIT_ENV})
        with open(log, "w") as f:
            subprocess.run(["claude", "-p", prompt, "--plugin-dir", plugin, "--model", model, "--max-turns", "3",
                            "--output-format", "stream-json", "--verbose", "--setting-sources", "project",
                            "--disallowedTools", "Write Edit Agent NotebookEdit"],
                           cwd=repo, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.DEVNULL, timeout=400)
    return pid, fired(log)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plugin", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--probe", action="append", choices=sorted(PROBES))
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("-j", type=int, default=8)
    ap.add_argument("--out", default=os.path.join(EVALS, "results", "routing"))
    a = ap.parse_args()
    out = os.path.join(a.out, a.model)
    os.makedirs(out, exist_ok=True)
    jobs = [(pid, n, os.path.abspath(a.plugin), a.model, out) for pid in (a.probe or sorted(PROBES))
            for n in range(1, a.runs + 1)]
    with ThreadPoolExecutor(a.j) as pool:
        done = list(pool.map(lambda j: run_one(*j), jobs))
    by_probe, cost = {}, 0.0
    for pid, (names, c) in done:
        by_probe.setdefault(pid, []).append(names)
        cost += c
    failed = 0
    for pid, runs in sorted(by_probe.items()):
        _, _, _, expect, forbid = PROBES[pid]
        ok = all(all(s in names for s in expect) and not any(s in names for s in forbid) for names in runs)
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'} {pid:20} expect {expect} forbid {forbid} | loaded {runs}")
    print(f"{len(by_probe) - failed}/{len(by_probe)} probes pass on {a.model}, cost ${cost:.2f}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
