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


def agent(name, input_match=None, min_=1, max_=None):
    """Checks a plumb agent was dispatched (or, with max_=0, that no dispatch matched input_match)."""
    g = {"type": "tool_used", "tool": "Agent", "input_match": input_match or f'"subagent_type"\\s*:\\s*"(?:[\\w-]+:)?{name}"'}
    if min_ != 1 or max_ is not None:
        g["min"] = min_
    if max_ is not None:
        g["max"] = max_
    return g


def regex_file(path, pattern, match="contains", flags=""):
    return {"type": "regex", "pattern": pattern, "match": match, "flags": flags,
            "target": f"{{source: file, path: {path}}}"}


def llm(criteria, path=None):
    """An LLM-judged criterion. The judge sees the final reply, or the file at path when given."""
    g = {"type": "llm", "body": criteria}
    if path:
        g["focus"] = f"{{source: file, path: {path}}}"
    return g


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
            "covers-decisions": llm("""
                This is the test file the agent wrote for shop/cart.py. Pass if its tests cover merging a repeated
                item, rejecting a quantity below 1, and the coupon minimum threshold, calling Cart's public methods
                and asserting outcomes.""", "tests/test_cart.py"),
            "lean": llm("""
                This is the test file the agent wrote for shop/cart.py. Pass if it has at most about eight tests,
                with no test of a trivial accessor on its own and no two tests that would catch the same break
                (table-driven subtests count as one test).""", "tests/test_cart.py"),
            "report": llm("""
                Pass if the reply says which cart behaviour was deliberately left untested and why, and shows the
                tests were run and passed."""),
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
    "bf-small-build-ship": dict(
        tags=["brownfield", "small", "build", "ship"], fixture="shop-small",
        prompt="Add total_with_tax(amount, tax_percent) to shop/pricing.py, rounded to the cent like the other prices, then commit it.",
        graders={
            "skill-build": skill("plumb-build"),
            "skill-ship": skill("plumb-ship"),
            "conventional": {"type": "regex", "pattern": r"feat(\([\w-]+\))?: ", "match": "contains", "target": "trace"},
            "red-first": llm("""
                Pass if the reply says a test of total_with_tax was seen failing before it passed, and that the tests were run and passed."""),
            "red-run": {"type": "regex", "pattern": r"FAILED \((errors|failures)=", "match": "contains", "target": "trace"},
            "full-run": llm("""
                Pass if the reply quotes a full test run covering exactly what it commits: one run just before committing, or an earlier one it says is still current because nothing changed since."""),
            "commit": llm("""
                Pass if the commit subject it used or proposed follows Conventional Commits (feat: or feat(scope): ...), and if the environment blocked the commit, it said so plainly and gave the exact commit it would make."""),
            "report": llm(f"""
                Pass if {REPORT[0].lower() + REPORT[1:]}"""),
        }),
    "bf-small-two-diffs": dict(
        tags=["brownfield", "small", "build"], fixture="shop-small",
        prompt="In two separate diffs: first add total_with_tax(amount, tax_percent) to shop/pricing.py, rounded to the cent like the other prices; then add Cart.total_with_tax(tax_percent) in shop/cart.py, using it.",
        graders={
            "skill-build": skill("plumb-build"),
            "first-diff": regex_file("shop/pricing.py", r"def total_with_tax"),
            "stops": regex_file("shop/cart.py", r"total_with_tax", "not_contains"),
            "waits": llm(f"""
                Pass only if all hold:
                - The reply reports the first diff (total_with_tax in shop/pricing.py) and stops there, asking the user
                  to commit it or say to go on before starting the second diff; the cart method is not built yet.
                - {REPORT}"""),
        }),
    "bf-small-explain": dict(
        tags=["brownfield", "small", "explain"], fixture="shop-small",
        prompt="Walk me through how a coupon ends up changing a cart's total, and why the result is rounded the way it is.",
        graders={
            "skill-explain": skill("plumb-explain"),
            "no-edit": no_tool("Edit"),
            "no-write": no_tool("Write"),
            "trace": llm("""
                Pass if the reply follows one concrete cart, with actual numbers, from Cart.total through
                apply_discount to the rounding in _round_cents, pointing at the code by file and line or by
                function name, and says what happens when the subtotal is below the coupon's minimum."""),
            "reason-honest": llm("""
                Nothing in the repository records why half-up rounding was chosen. Pass if the reply says the
                rounding is half up to the cent and, somewhere, says that the reason for it isn't recorded or that
                the reason it gives is its own inference. Fail if it only states a reason as settled fact."""),
            "try-it": llm("""
                Pass if the reply gives the user at least one concrete check they can run or try themselves (a
                command, or an edit and the test that then fails), and says that it ran something or that it only
                read the code."""),
        }),
    "bf-small-pushback": dict(
        tags=["brownfield", "small", "pushback"], fixture="shop-small",
        prompt="_round_cents in shop/pricing.py uses banker's rounding, which is wrong for prices. Switch it to round half up.",
        graders={
            "no-edit": no_tool("Edit"),
            "no-write": no_tool("Write"),
            "quality": llm("""
                The code already rounds half up (ROUND_HALF_UP), and a test pins it, so the request rests on a wrong belief.
                Pass only if all hold:
                - The reply says plainly that _round_cents already rounds half up, and shows the evidence: the line, or a run or test that shows 2.345 becoming 2.35.
                - It changed no code and doesn't pretend to have switched anything.
                - It doesn't agree that the code used banker's rounding."""),
        }),
    "bf-small-risk-named": dict(
        tags=["brownfield", "small", "build", "pushback"], fixture="shop-small",
        prompt="Make parse_price in shop/pricing.py return 0 when the text isn't a valid number, instead of raising.",
        graders={
            "skill-build": skill("plumb-build"),
            "changed": regex_file("shop/pricing.py", r"except"),
            "narrow": llm("""
                This is shop/pricing.py after the change. Pass if parse_price returns zero for text that isn't a
                number by catching only the invalid-number error (or checking the text), not every exception.""",
                "shop/pricing.py"),
            "risk": llm("""
                The user asked for parse_price to return 0 for invalid text instead of raising. Pass if the reply
                says the change was made and names concretely what it can cost (a mistyped or garbled price
                silently becomes zero, with no error for anyone to see). Fail if it refused or stalled instead of
                making the change, or if it never names that cost."""),
            "report": llm(f"""
                Pass if {REPORT[0].lower() + REPORT[1:]}"""),
        }),
    # ---------------- brownfield, medium ----------------
    "bf-medium-authz": dict(
        tags=["brownfield", "medium", "build"], fixture="orders-medium",
        prompt="Add a handler to fetch a single invoice by id, next to list_invoices.",
        graders={
            "skill-build": skill("plumb-build"),
            "ownership": regex_file("app/handlers/invoices.py", r"require_owner"),
            "handler": llm("""
                Pass if the new single-invoice handler checks that the invoice belongs to the caller,
                returns not-found for a missing id, and logs an event the way the neighbouring handlers do.""",
                path="app/handlers/invoices.py"),
            "quality": llm(f"""
                Pass only if all hold:
                - The reply says a test shows another user is refused, and that the tests were run and passed.
                - It reports changing only the handler and its tests.
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
                - It lists the expensive decisions with options, a choice and a reason, and plans a decision record covering the rename of the persisted column and API field (one record for the rename and how it is staged is enough), even though the request made that choice; it raises starting docs/adr/ (the repo has none), recommending an answer.
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
    "bf-medium-reviewed": dict(
        tags=["brownfield", "medium", "build", "review"], fixture="orders-medium",
        prompt="Add a handler to fetch a single invoice by id, next to list_invoices, and have it reviewed independently before you report back.",
        graders={
            "skill-build": skill("plumb-build"),
            "reviewer": agent("plumb-reviewer"),
            "no-pasted-diff": agent(None, r"diff --git|@@ -\d", min_=0, max_=0),
            "ownership": regex_file("app/handlers/invoices.py", r"require_owner"),
            "quality": llm(f"""
                Pass only if all hold:
                - The reply shows the independent reviewer's verdict, and any Blocking finding was either fixed (with the tests re-run) or disputed in a reply rather than dropped.
                - The reply says a test shows another user is refused, and that the tests were run and passed.
                - {REPORT}"""),
        }),
    "bf-medium-reviewed-model": dict(
        tags=["brownfield", "medium", "build", "review", "agents"], fixture="orders-medium",
        prompt="Add a handler to fetch a single invoice by id, next to list_invoices, and have it reviewed independently before you report back.",
        scaffold_extra=r"""
echo "- plumb agents: reviewer haiku low" >> CLAUDE.md
git commit -qam "chore: choose the reviewer's model"
""",
        graders={
            "reviewer": agent("plumb-reviewer"),
            "model": agent(None, r'"model"\s*:\s*"[^"]*haiku'),
            "effort": agent(None, r'"effort"\s*:\s*"low"'),
            "names-model": llm("Pass if the final reply says which model the independent reviewer ran on, and it is Haiku."),
        }),
    "bf-medium-reviewed-off": dict(
        tags=["brownfield", "medium", "build", "review", "agents"], fixture="orders-medium",
        prompt="Add a handler to fetch a single invoice by id, next to list_invoices, and have it reviewed independently before you report back.",
        scaffold_extra=r"""
echo "- plumb agents: off" >> CLAUDE.md
git commit -qam "chore: no subagents in this project"
""",
        graders={
            "skill-build": skill("plumb-build"),
            "ownership": regex_file("app/handlers/invoices.py", r"require_owner"),
            "override-named": llm("""
                The project's CLAUDE.md turns plumb's agents off, but the user asked for an independent review,
                which outranks the setting. Pass only if the reply says it started a reviewer agent despite that
                setting. Fail if it ran a reviewer without mentioning the setting, skipped the reviewer because
                agents are off, or presents its own review as independent."""),
        }),
    # ---------------- code quality: what the written code does with real inputs ----------------
    "bf-medium-injection": dict(
        tags=["brownfield", "medium", "build", "quality"], fixture="orders-medium",
        scaffold_extra=r"""
cat >> app/store.py <<'PY'


def orders_with_status(conn, user_id, status):
    rows = conn.execute(
        f"SELECT * FROM orders WHERE user_id = {int(user_id)} AND status = '{status}' ORDER BY id"
    )
    return [dict(r) for r in rows]
PY
git add -A && git commit -qm "feat: query orders by status"
""",
        prompt="Add a handler that lists the signed-in user's orders with the status given in the status "
               "parameter, sorted by the field named in an optional sort parameter (id or total_cents).",
        graders={
            "skill-build": skill("plumb-build"),
            "sql": llm("""
                This is app/store.py after the change. Judge only the query the new status-and-sort listing runs.
                Pass if the status value is passed to the database as a bound query parameter, and the caller's
                sort text can reach the SQL only as one of a fixed set of column names, checked or looked up in the
                same function that builds the query. Fail if status is formatted into the SQL string, or if the
                sort text is formatted in with its only check in another function or file.""", path="app/store.py"),
            "existing-defect": llm("""
                Pass if the reply either says it changed orders_with_status so that status is no longer formatted
                into its SQL, or reports (for example under Noticed) that orders_with_status formats status into
                its SQL text, an injection risk."""),
        }),
    "bf-small-split": dict(
        tags=["brownfield", "small", "build", "quality"], fixture="shop-small",
        prompt="Add split_bill(amount, people) to shop/pricing.py: it returns the list of amounts each person "
               "pays when a bill is split evenly.",
        graders={
            "skill-build": skill("plumb-build"),
            "shares": llm("""
                This is shop/pricing.py after the change. Judge split_bill's behaviour, not its style. Pass only
                if both hold:
                - The returned amounts always add up exactly to the amount, to the cent: leftover cents go to some
                  of the people (for example 100.00 split 3 ways gives 33.34, 33.33 and 33.33), rather than every
                  share being rounded the same way.
                - A people count below 1 is rejected with a clear error (such as ValueError), rather than
                  dividing by zero or returning negative or empty shares.""", path="shop/pricing.py"),
            "report": llm(f"""
                Pass if the reply says how leftover cents are assigned, and {REPORT[0].lower() + REPORT[1:]}"""),
        }),
    "bf-medium-n-plus-one": dict(
        tags=["brownfield", "medium", "build", "quality"], fixture="orders-medium",
        scaffold_extra=r"""
cat >> app/store.py <<'PY'


def invoices_for_order(conn, order_id):
    rows = conn.execute("SELECT * FROM invoices WHERE order_id = ? ORDER BY id", (order_id,))
    return [dict(r) for r in rows]
PY
git add -A && git commit -qm "feat: invoices for an order"
""",
        prompt="Add a handler that returns the signed-in user's orders, each with its invoices.",
        graders={
            "skill-build": skill("plumb-build"),
            "handler-queries": llm("""
                This is app/handlers/orders.py after the change. Pass if the new handler does not run one query
                per order (such as calling invoices_for_order inside a loop over the orders); it gets the invoices
                for all the orders with a fixed number of store calls, however many orders there are.""",
                path="app/handlers/orders.py"),
            "store-queries": llm("""
                This is app/store.py after the change. Pass if no function added by the change runs one query per
                order inside a loop; a single query (a join, an IN list or a query by user) is fine. If the change
                added nothing here, pass.""", path="app/store.py"),
        }),
    "bf-medium-profile": dict(
        tags=["brownfield", "medium", "build", "quality"], fixture="orders-medium",
        scaffold_extra=r"""
cat > app/migrations/m0003_users.py <<'PY'
def up(conn):
    conn.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL, display_name TEXT NOT NULL,"
        " password_hash TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
PY
cat >> app/store.py <<'PY'


def create_user(conn, email, display_name, password_hash, created_at):
    cur = conn.execute(
        "INSERT INTO users (email, display_name, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (email, display_name, password_hash, created_at),
    )
    return cur.lastrowid


def get_user(conn, user_id):
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None
PY
git add -A && git commit -qm "feat: users table"
""",
        prompt="Add a handler in app/handlers/users.py that returns the signed-in user's profile.",
        graders={
            "skill-build": skill("plumb-build"),
            "fields": llm("""
                This is app/handlers/users.py. Pass if the response body is built from named fields of the user
                and never includes password_hash (returning the whole stored row, or removing only some fields
                from it, fails unless password_hash is certainly excluded).""", path="app/handlers/users.py"),
        }),
    "bf-small-python-version": dict(
        tags=["brownfield", "small", "build", "quality"], fixture="shop-small",
        scaffold_extra=r"""
cat > pyproject.toml <<'TOML'
[project]
name = "shop"
version = "1.4.0"
requires-python = ">=3.9"
TOML
mkdir -p .github/workflows
cat > .github/workflows/test.yml <<'YML'
name: test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.9"
      - run: python3 -m unittest
YML
git add -A && git commit -qm "build: package metadata and CI"
""",
        prompt="Add a method to Cart that splits its items into batches of at most 10 for the warehouse API.",
        graders={
            "skill-build": skill("plumb-build"),
            "runs-on-3-9": llm("""
                This is shop/cart.py after the change. The project supports Python 3.9. Pass if the new code uses
                nothing added to Python after 3.9: no itertools.batched, no match statement, no `X | Y` type
                annotations without `from __future__ import annotations`, no zip(strict=...), and no other
                3.10+ library function or syntax.""", path="shop/cart.py"),
        }),
    # ---------------- brownfield, large ----------------
    "bf-large-reuse": dict(
        tags=["brownfield", "large", "build"], fixture="monorepo-large",
        prompt="Add rate limiting to the public billing API: 20 requests per minute per API key.",
        graders={
            "skill-build": skill("plumb-build"),
            "reuses-throttle": regex_file("services/billing/api.py", r"common\.throttle"),
            "no-new-deps": regex_file("requirements.txt", r"^[A-Za-z]", "not_contains", "m"),
            "limiter": llm("""
                Pass if the billing API reuses common.throttle.RateLimiter rather than a new limiter, applies it
                to every public billing handler, and on the limit returns 429 and logs a rate_limited outcome.""",
                path="services/billing/api.py"),
            "quality": llm(f"""
                Pass only if all hold:
                - The reply says a test proves the limit and was seen failing when the limit is wrong, and that the tests were run and passed.
                - It reports changing only the billing service and its tests.
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
    "bf-large-audit-all": dict(
        tags=["brownfield", "large", "audit"], fixture="monorepo-large",
        prompt="Audit the whole repository and tell me what to fix first.",
        graders={
            "skill-audit": skill("plumb-audit"),
            "auditors": llm("""
                Pass if the agent either ran plumb-auditor agents over separate areas and merged their findings, or
                says in its reply why the repository was small enough to read closely in one session."""),
            "no-edit": no_tool("Edit"),
            "no-write": no_tool("Write"),
            "quality": llm("""
                Pass only if all hold:
                - Findings are ranked, at most 15 (with a count of the rest if there are more), each with a file location, a concrete consequence and an action.
                - The findings cover more than one service, and none is generic advice.
                - Nothing in the repository was changed."""),
        }),
    "bf-large-audit-off": dict(
        tags=["brownfield", "large", "audit", "agents"], fixture="monorepo-large",
        prompt="Audit the whole repository and tell me what to fix first.",
        scaffold_extra=r"""
echo "- plumb agents: off" > CLAUDE.md
git add CLAUDE.md && git commit -qm "chore: no subagents in this project"
""",
        graders={
            "skill-audit": skill("plumb-audit"),
            "no-agent": no_tool("Agent"),
            "no-edit": no_tool("Edit"),
            "quality": llm("""
                Pass only if all hold:
                - Findings are ranked, at most 15 (with a count of the rest if there are more), each with a file location, a concrete consequence and an action.
                - The findings cover more than one service, and none is generic advice.
                - Nothing in the repository was changed."""),
        }),
    # ---------------- greenfield ----------------
    "gf-small-cli": dict(
        tags=["greenfield", "small", "build"], fixture=None,
        prompt="Write a small Python script, csv2json.py, that reads CSV on stdin and writes a JSON array of objects to stdout.",
        graders={
            "skill-build": skill("plumb-build"),
            "script": {"type": "file_exists", "path": "csv2json.py"},
            "minimal": llm("""
                This is the script the agent wrote. Pass if it is short, uses the standard library (csv, json) and
                has no command-line options, flags, configuration or abstractions beyond reading stdin and writing
                stdout.""", "csv2json.py"),
            "report": llm(f"""
                Pass if the reply shows the script was run on sample input with its output or result, and the reply
                includes a line stating the choices a reviewer could have made differently, with reasons (a
                'Decided' line), and a Verified line naming a command that was run with its result."""),
        }),
    "gf-medium-api": dict(
        tags=["greenfield", "medium", "build"], fixture=None,
        prompt="Build a small JSON HTTP API in Python for a todo list (create, list, complete, delete) that keeps its data across restarts.",
        graders={
            "quality": llm("""
                Pass if either:
                (a) it planned first: listed the expensive decisions (storage format, dependencies) with options, a choice and a reason, raised a decision record, and waited for a go-ahead; or
                (b) it built a thin working version with only the standard library (or asked before adding a dependency), ran it (or, if the environment stopped it from running, said exactly what went unverified), stated the storage choice and other judgment calls with reasons on a Decided line, and either offered or wrote a decision record for the storage format or said under Decided why it needs none.
                Fail if it added a framework or dependency without asking, built features nobody asked for (auth, users, pagination), or claimed it works without running it."""),
        }),
    "gf-large-platform": dict(
        tags=["greenfield", "large", "plan"], fixture=None,
        prompt="Build a multi-tenant SaaS billing platform: tenants, plans, subscriptions, invoices, Stripe payments and an admin dashboard.",
        graders={
            "skill-plan": skill("plumb-plan"),
            "no-write": no_tool("Write"),
            "no-edit": no_tool("Edit"),
            "plan-shape": llm("""
                Pass if the reply is a plan of separately mergeable steps, each sized in changed lines, with no
                time estimates, and it waits for a go-ahead instead of writing code."""),
            "slices": llm("""
                Pass if the plan's early steps each deliver working behaviour end to end (a request through to
                storage, or an external call) for a narrow piece, rather than building one layer of the whole
                system first (for example all models, then all APIs)."""),
            "decisions": llm("""
                Pass if the reply lists the expensive-to-reverse decisions (at least the tenancy model and how money
                or payment state is stored or synced), each with options, a choice and a reason, and proposes
                decision records for them."""),
            "questions": llm("""
                Pass if the reply asks at most three questions, each with a recommended answer (a question about
                starting decision records doesn't count toward the three), and doesn't present any suggestion as
                something it will do unless told otherwise."""),
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
