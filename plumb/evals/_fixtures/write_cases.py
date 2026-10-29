"""Writes plumb's eval cases (prompt.md, case.yaml, scaffold.sh, graders/) from the table below.

Run from plumb/evals: python3 _fixtures/write_cases.py
Edit the table and re-run, rather than editing the generated case folders by hand.
"""
import os
import shutil
import textwrap

TOOLS = "[Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]"


def skill(name):
    return {"type": "tool_used", "tool": "Skill", "input_match": f'"skill"\\s*:\\s*"(?:[\\w-]+:)?{name}"'}


def no_tool(tool, input_match=None):
    g = {"type": "tool_used", "tool": tool, "min": 0, "max": 0}
    if input_match:
        g["input_match"] = input_match
    return g


def regex_file(path, pattern, match="contains", flags=""):
    return {"type": "regex", "pattern": pattern, "match": match, "flags": flags,
            "target": f"{{source: file, path: {path}}}"}


def llm(criteria):
    return {"type": "llm", "body": criteria}


REPORT = ("The final reply ends with plumb's report or an equivalent receipt that includes a line stating the "
          "choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line "
          "quoting a command that was actually run with its result.")

CASES = {
    # ---------------- brownfield, small ----------------
    "bf-small-debug": dict(
        tags=["brownfield", "small", "debug"], fixture="shop-small",
        prompt="Customers who type a price like 1,200.50 get a crash from parse_price. Fix it.",
        graders={
            "skill-debug": skill("plumb-debug"),
            "no-swallow": regex_file("shop/pricing.py", r"except", "not_contains"),
            "regression-test": regex_file("tests/test_pricing.py", r"1,200"),
            "quality": llm(f"""
                Pass only if all hold:
                - The reply names the cause (the thousands separator is not removed before Decimal parses the text).
                - The fix is in parse_price itself, small, and doesn't catch or hide the error.
                - Exactly one regression test was added for the comma case, and the reply says it was seen failing before the fix.
                - No unrelated code was changed or reformatted.
                - {REPORT}"""),
        }),
    "bf-small-tests": dict(
        tags=["brownfield", "small", "test"], fixture="shop-small",
        prompt="Add tests for shop/cart.py.",
        graders={
            "skill-test": skill("plumb-test"),
            "test-file": {"type": "file_exists", "path": "tests/test_cart*.py"},
            "quality": llm("""
                Pass only if all hold:
                - The tests cover cart behaviour with real decisions: merging repeated items, rejecting quantity below 1, and the coupon minimum threshold.
                - There are no tests of trivial accessors or of Python itself, and no near-duplicates; at most about eight tests in total, with same-shape cases sharing one table-driven test.
                - Tests go through Cart's public methods and assert outcomes, not internal list layout beyond what callers rely on.
                - The reply names in one line what was deliberately left untested and why.
                - The reply shows the tests were run and passed."""),
        }),
    "bf-small-refactor": dict(
        tags=["brownfield", "small", "refactor"], fixture="shop-small",
        prompt="Inline the _round_cents helper in shop/pricing.py; it is only a one-liner.",
        graders={
            "skill-refactor": skill("plumb-refactor"),
            "quality": llm("""
                The helper is used twice, and tests/test_pricing.py has a test that calls _round_cents directly.
                Pass if either:
                (a) the agent inlined it, and the rounding behaviour is still pinned by a test through a public function
                    (format_price or apply_discount) that the reply says was seen red, the old internal test was
                    re-pointed rather than simply deleted, and the reply states behaviour is unchanged with the checks run; or
                (b) the agent explains that inlining duplicates the rounding rule in two places and asks or recommends
                    keeping it, without changing code.
                Fail if the rounding test was deleted with no replacement, any assertion was loosened, or behaviour changed."""),
        }),
    "bf-small-ship": dict(
        tags=["brownfield", "small", "ship"], fixture="shop-small",
        scaffold_extra=r"""
python3 - <<'PY'
p = "shop/pricing.py"
s = open(p).read()
s += '''

def total_with_tax(amount, tax_percent):
    # Adds sales tax, rounded to the cent.
    return _round_cents(amount * (Decimal(100) + Decimal(tax_percent)) / Decimal(100))
'''
open(p, "w").write(s)
t = "tests/test_pricing.py"
s = open(t).read().replace('''

if __name__''', '''
    def test_total_with_tax_rounds_half_up(self):
        self.assertEqual(pricing.total_with_tax(Decimal("10.05"), 10), Decimal("11.06"))


if __name__''')
open(t, "w").write(s)
PY
""",
        prompt="Commit this.",
        graders={
            "skill-ship": skill("plumb-ship"),
            "conventional": {"type": "regex", "pattern": r"feat(\([\w-]+\))?: ", "match": "contains", "target": "trace"},
            "quality": llm("""
                Pass only if all hold:
                - The agent read the change and ran the project's tests before committing, and quotes the result.
                - The commit subject it used or proposed follows Conventional Commits (feat: or feat(scope): ...), is in the imperative and describes the behaviour added.
                - If the environment blocked the commit, it said so plainly and gave the exact commit it would make.
                - It didn't push, open a pull request or change code."""),
        }),
    # ---------------- brownfield, medium ----------------
    "bf-medium-authz": dict(
        tags=["brownfield", "medium", "build"], fixture="orders-medium",
        prompt="Add a handler to fetch a single invoice by id, next to list_invoices.",
        graders={
            "skill-build": skill("plumb-build"),
            "ownership": regex_file("app/handlers/invoices.py", r"require_owner"),
            "quality": llm(f"""
                Pass only if all hold:
                - The new handler checks that the invoice belongs to the caller (require_owner), returns not-found for a missing id, and logs one event like its neighbours.
                - A test shows another user is refused; tests were run and passed.
                - The diff is limited to the handler and its tests.
                - {REPORT}"""),
        }),
    "bf-medium-consumer": dict(
        tags=["brownfield", "medium", "build"], fixture="orders-medium",
        prompt="Add a consumer that marks an order paid when a payment.succeeded event arrives.",
        graders={
            "skill-build": skill("plumb-build"),
            "consumer-file": {"type": "file_exists", "path": "app/consumers/*pay*.py"},
            "quality": llm(f"""
                Pass only if all hold:
                - The consumer is safe on redelivery (the broker delivers at least once, as the shipping consumer documents): a duplicate event doesn't fail or change state twice, and an unknown order is handled as the shipping consumer handles it.
                - It follows the shipping consumer's conventions (store.set_status, one log event per message with an outcome).
                - A test covers redelivery, and tests were run and passed.
                - {REPORT}"""),
        }),
    "bf-medium-plan": dict(
        tags=["brownfield", "medium", "plan"], fixture="orders-medium",
        prompt="Rename the order status field to state everywhere, including the database column.",
        graders={
            "skill-plan": skill("plumb-plan"),
            "no-edit": no_tool("Edit"),
            "no-write": no_tool("Write"),
            "quality": llm("""
                Pass only if all hold:
                - The agent produced a plan and did not change code yet, waiting for a go-ahead.
                - Because the column is persisted data, the plan stages it (add the new column, migrate or dual-write, then remove the old), with migrations in app/migrations/ as the project's rules require.
                - It lists the expensive decisions with options, a choice and a reason, and raises keeping a decision record (the repo has no docs/adr/), recommending an answer.
                - Questions, if any, are at most three, each with a recommended answer."""),
        }),
    "bf-medium-review": dict(
        tags=["brownfield", "medium", "review"], fixture="orders-medium",
        scaffold_extra=r"""
git checkout -q -b feature/loyalty-cap
python3 - <<'PY'
p = "app/discounts.py"
s = open(p).read().replace("capped at 10%", "capped at 15%").replace("min(years_as_customer * 2, 10)", "min(years_as_customer * 2, 15)")
open(p, "w").write(s)
t = "tests/test_discounts.py"
s = open(t).read().replace("(1000, 3, 60), (1000, 9, 100)", "(1000, 3, 60)")
open(t, "w").write(s)
PY
git commit -qam "feat: raise loyalty discount cap to 15%

Tests pass."
""",
        prompt="Review the feature/loyalty-cap branch against main before I merge it.",
        graders={
            "skill-review": skill("plumb-review"),
            "no-edit": no_tool("Edit"),
            "verdict": {"type": "regex", "pattern": "request changes", "flags": "i", "match": "contains"},
            "quality": llm("""
                Pass only if all hold:
                - The verdict is request changes.
                - A Blocking finding says the test row that pinned the cap (9 years -> 100) was deleted instead of updated, so the changed cap is now untested, and the fix is to assert the new cap (for example 9 years -> 150).
                - The review ran or traced the tests rather than trusting "Tests pass".
                - It changed no files."""),
        }),
    "bf-medium-ship-red": dict(
        tags=["brownfield", "medium", "ship"], fixture="orders-medium",
        scaffold_extra=r"""
sed -i 's/min(years_as_customer \* 2, 10)/min(years_as_customer * 2, 12)/' app/discounts.py
""",
        prompt="Commit this.",
        graders={
            "skill-ship": skill("plumb-ship"),
            "not-committed": no_tool("Bash", "git commit"),
            "quality": llm("""
                Pass only if all hold:
                - The agent ran the tests, saw the discount test fail because of the uncommitted change, and did not commit.
                - It reports the failure and asks how to proceed (update the test for the new cap, or revert), without changing code itself.
                - Any commit message it proposes follows Conventional Commits."""),
        }),
    # ---------------- brownfield, large ----------------
    "bf-large-reuse": dict(
        tags=["brownfield", "large", "build"], fixture="monorepo-large",
        prompt="Add rate limiting to the public billing API: 20 requests per minute per API key.",
        graders={
            "skill-build": skill("plumb-build"),
            "reuses-throttle": regex_file("services/billing/api.py", r"common\.throttle"),
            "no-new-deps": regex_file("requirements.txt", r"^[A-Za-z]", "not_contains", "m"),
            "quality": llm(f"""
                Pass only if all hold:
                - It reuses common.throttle.RateLimiter rather than writing a new limiter, and follows the search API's pattern (429 response, a rate_limited log outcome).
                - Both billing handlers are limited, and a test with a controlled clock proves the limit; tests were run and passed.
                - Nothing outside the billing service was changed.
                - {REPORT}"""),
        }),
    "bf-large-audit": dict(
        tags=["brownfield", "large", "audit"], fixture="monorepo-large",
        prompt="Audit the tests in tests/billing: which are useless, and what's missing?",
        graders={
            "skill-audit": skill("plumb-audit"),
            "no-edit": no_tool("Edit"),
            "no-write": no_tool("Write"),
            "quality": llm("""
                Pass only if all hold:
                - test_dict_has_keys is marked for deletion (it tests Python, not billing).
                - test_build_totals_again is marked as a duplicate to merge or delete.
                - test_build_matches_formula is flagged for computing the expected value the way the code does.
                - The missing tests named include proration.credit_cents (rounding down, the days_in_period guard), ranked by risk.
                - Findings are ranked, concrete, and nothing was changed."""),
        }),
    # ---------------- greenfield ----------------
    "gf-small-cli": dict(
        tags=["greenfield", "small", "build"], fixture=None,
        prompt="Write a small Python script that reads CSV on stdin and writes a JSON array of objects to stdout.",
        graders={
            "skill-build": skill("plumb-build"),
            "script": {"type": "file_exists", "path": "*.py"},
            "quality": llm(f"""
                Pass only if all hold:
                - One short script using the standard library (csv, json), with no options, flags, config or abstractions nobody asked for.
                - It was run on sample input and the output shown.
                - No more than a minimal test or two, and no extra files such as a README or notes unless asked.
                - {REPORT}"""),
        }),
    "gf-medium-api": dict(
        tags=["greenfield", "medium", "build"], fixture=None,
        prompt="Build a small JSON HTTP API in Python for a todo list (create, list, complete, delete) that keeps its data across restarts.",
        graders={
            "quality": llm("""
                Pass if either:
                (a) it planned first: listed the expensive decisions (storage format, dependencies) with options, a choice and a reason, raised a decision record, and waited for a go-ahead; or
                (b) it built a thin working version with only the standard library (or asked before adding a dependency), ran it (or, if the environment stopped it from running, said exactly what went unverified), stated the storage choice and other judgment calls with reasons on a Decided line, and offered or wrote a decision record for the storage format.
                Fail if it added a framework or dependency without asking, built features nobody asked for (auth, users, pagination), or claimed it works without running it."""),
        }),
    "gf-large-platform": dict(
        tags=["greenfield", "large", "plan"], fixture=None,
        prompt="Build a multi-tenant SaaS billing platform: tenants, plans, subscriptions, invoices, Stripe payments and an admin dashboard.",
        graders={
            "skill-plan": skill("plumb-plan"),
            "no-write": no_tool("Write"),
            "no-edit": no_tool("Edit"),
            "quality": llm("""
                Pass only if all hold:
                - It produced a plan of small, separately mergeable steps instead of writing code, and waits for a go-ahead.
                - The first behaviour step is a thin end-to-end slice, not a layer.
                - Expensive decisions (tenancy model, data store, money representation, payment provider integration) are listed with options, a choice and a reason, and decision records are proposed.
                - It asks at most three questions, each with a recommended answer, and has no time estimates."""),
        }),
}


def frontmatter(d):
    lines = ["---"]
    for k, v in d.items():
        if k == "body" or v == "":
            continue
        if isinstance(v, str) and k in ("pattern", "input_match", "path") and not v.startswith("{"):
            v = "'" + v.replace("'", "''") + "'"
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def main():
    here = os.getcwd()
    for name, case in CASES.items():
        d = os.path.join(here, name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(os.path.join(d, "graders"))
        tags = "[" + ", ".join(case["tags"]) + "]"
        with open(os.path.join(d, "prompt.md"), "w") as f:
            f.write(f"---\nname: {name}\ntags: {tags}\nruns: 1\nmax_turns: 60\ntimeout_seconds: 1200\n"
                    f"allowed_tools: {TOOLS}\n---\n{case['prompt']}\n")
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write(f'schema_version: "1.1"\nname: {name}\n')
            if case["fixture"]:
                f.write("context:\n  scaffold_script: scaffold.sh\n")
        if case["fixture"]:
            path = os.path.join(d, "scaffold.sh")
            with open(path, "w") as f:
                f.write("#!/bin/bash\nset -euo pipefail\n")
                f.write(f'. "$(dirname "$0")/../_fixtures/seed.sh" {case["fixture"]}\n')
                f.write(case.get("scaffold_extra", ""))
            os.chmod(path, 0o755)
        graders = dict(case["graders"], **{"skill-charter": skill("plumb")})
        for gname, g in graders.items():
            with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
                f.write(frontmatter(g))
                if "body" in g:
                    f.write(textwrap.dedent(g["body"]).strip() + "\n")


if __name__ == "__main__":
    main()
