"""Runs build tasks in writable repositories and grades what was built, not what the reply says about it.

`claude plugin eval` grades the final reply and files as text. A reply can describe a timeout the code
doesn't have, and a suite can pass while a mutant of the code survives it. This runner builds each case's
fixture in a temporary git repository, runs `claude -p` in it, then uses the result as a stranger would:
it calls the handler against a carrier that drips or truncates its answer, sends badly framed requests to
the new route, puts the bug back and reruns the tests, moves a boundary by one, and reads the commits the
session left. Checks that need judgement (a report's Suggestions, a commit body) go to a judge model with
one question each.

Each arm is a copy of the plugin, so a wording change is measured against main directly:

  python3 _built/run.py --model <agent model> --judge <the strongest model> --runs 3 \
      --arm main=/path/to/main/plumb --arm new=/path/to/branch/plumb [--arm without] [--case carrier ...]

Run from plumb/evals. Needs the `claude` CLI on PATH. Each run is a full agent session. A check prints
passes over the runs that could be measured; a run where the probe couldn't reach what it tests (no
handler, no commit) is left out of that check and counted, never scored as a pass or a fail.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(EVALS, "_fixtures"))
sys.path.insert(0, os.path.join(EVALS, "_harm"))
import run as harm  # noqa: E402
from write_cases import CASES as SUITE  # noqa: E402

TESTS = {"orders-medium": "python3 -m unittest discover -s tests -t .", "shop-small": "python3 -m unittest",
         "todo-web": "python3 -m unittest", "monorepo-large": "python3 -m unittest"}
AGENTS_OFF = 'echo "- plumb agents: off" >> CLAUDE.md\ngit commit -qam "chore: no subagents in this project"\n'


class Run:
    """One finished session: its repository, the commit it started from and its replies, in turn order."""

    def __init__(self, repo, start, replies, fixture, judge_model, log):
        self.repo, self.start, self.replies, self.fixture = repo, start, replies, fixture
        self.judge_model, self.log = judge_model, log

    def sh(self, cmd, cwd=None, timeout=300, env=None):
        try:
            return subprocess.run(["bash", "-c", cmd], cwd=cwd or self.repo, capture_output=True, text=True,
                                  timeout=timeout, env={**os.environ, **harm.GIT_ENV, **(env or {})})
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(cmd, 124, "", "timed out")

    def probe(self, name, *args, timeout=120):
        out = self.sh(f"{sys.executable} -B {os.path.join(HERE, name)} {' '.join(args)}", timeout=timeout).stdout
        lines = [line for line in out.splitlines() if line.startswith("{")]
        return json.loads(lines[-1]) if lines else None

    def inline(self, source):
        """Runs a probe given as source, from the repository, without leaving a file in it."""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(source)
        try:
            return self.probe(f.name)
        finally:
            os.remove(f.name)

    def tests_pass(self, cwd=None, env=None):
        return self.sh(TESTS[self.fixture], cwd=cwd, env=env).returncode == 0

    def copy(self):
        """A scratch copy of the repository, for a check that changes the code."""
        dest = tempfile.mkdtemp(prefix="built-copy-")
        shutil.copytree(self.repo, os.path.join(dest, "repo"), symlinks=True)
        return os.path.join(dest, "repo")

    def commits(self):
        """Full messages of the commits the session made, oldest first."""
        return self.sh(f"git log --reverse --format='commit %h%n%B' {self.start}..HEAD").stdout.strip()

    def changes(self):
        """Everything the session changed: the diff from its start, and new files not yet tracked."""
        diff = self.sh(f"git diff {self.start}").stdout
        new = self.sh("git ls-files --others --exclude-standard | grep -v __pycache__ | head -20").stdout.split()
        return diff + "".join(f"\n--- new file {p} ---\n{open(os.path.join(self.repo, p), errors='replace').read()}"
                              for p in new if os.path.isfile(os.path.join(self.repo, p)))

    def judge(self, question, material):
        """One question to the judge model about the material. None when it gives no verdict."""
        prompt = (f"{question}\n\nGive one sentence of reasoning, then end with a line holding only PASS or FAIL."
                  f"\n\n<material>\n{material[:60000]}\n</material>")
        with tempfile.TemporaryDirectory() as empty:
            try:
                done = subprocess.run(["claude", "-p", prompt, "--model", self.judge_model, "--setting-sources",
                                       "project"], cwd=empty, stdin=subprocess.DEVNULL, capture_output=True,
                                      text=True, timeout=600)
            except subprocess.TimeoutExpired:
                return None
        with open(self.log + ".judge", "a") as f:
            f.write(f"## {question[:80]}\n{done.stdout}\n")
        verdict = re.findall(r"^\W*(PASS|FAIL)\W*$", done.stdout, re.M)
        return verdict[-1] == "PASS" if verdict else None


# ---------------- checks that run what was built ----------------

def carrier(run, scenario):
    """The probe's result for one carrier behaviour, or None when the handler can't be reached at all."""
    ok = run.probe("probe_carrier.py", "ok")
    if not ok or ok["outcome"] != "response:200" or not ok["hits"]:
        return None
    return run.probe("probe_carrier.py", scenario, timeout=150)


def carrier_deadline(run):
    """A carrier that sends one byte a second for a minute is cut off, not waited out."""
    got = carrier(run, "drip")
    return got and got["elapsed"] <= 30


def carrier_transport(run):
    """A truncated body and a non-HTTP answer reach the caller as the project's own failure."""
    verdicts = []
    for scenario in ("truncated", "garbage"):
        got = carrier(run, scenario)
        if got is None:
            return None
        outcome = got["outcome"]
        own = outcome.startswith("raised:app.") or (outcome.startswith("response:") and outcome[9:] >= "400")
        verdicts.append(own)
    return all(verdicts)


def carrier_timeout_held(run):
    """With the timeout argument deleted, a test goes red or the report lists the timeout as unchecked."""
    path = "app/handlers/shipping.py"
    source = open(os.path.join(run.repo, path)).read()
    mutant = re.sub(r",\s*timeout\s*=\s*[^,)]+", "", source, count=1)
    if mutant == source:
        return None
    copy = run.copy()
    open(os.path.join(copy, path), "w").write(mutant)
    red = not run.tests_pass(cwd=copy)
    shutil.rmtree(os.path.dirname(copy), ignore_errors=True)
    owned = re.search(r"unchecked.{0,600}?(time.?out|hang|slow|deadline)", run.replies[-1], re.I | re.S)
    return red or bool(owned)


def framing(run):
    """Every badly framed request to the new route gets a 4xx and the server serves the next one."""
    got = run.probe("probe_framing.py")
    if not got or not got["method"]:
        return None
    return all(r["status"] and 400 <= r["status"] < 500 and r["served_next"] for r in got["requests"].values())


FILTER_PROBE = r'''
import json, sys
sys.path.insert(0, ".")
from app import store
from app.db import connect
from app.handlers.orders import list_orders
from app.http import Request, Response
conn = connect()
for status in ("pending", "paid", "shipped"):
    store.set_status(conn, store.create_order(conn, 7, 100), status)
conn.commit()
def call(params):
    try:
        r = list_orders(conn, Request(7, params=params))
    except Exception as e:
        return "raised:" + type(e).__name__
    return [r.status, len(r.body) if isinstance(r.body, list) else -1] if isinstance(r, Response) else "other"
print(json.dumps({"good": call({"status": "paid"}), "misspelt": call({"statu": "paid"}),
                  "unknown": call({"status": "payed"})}))
'''


def order_filter(run):
    got = run.inline(FILTER_PROBE)
    return got if got and got["good"] == [200, 1] else None


def filter_told_apart(run):
    """A misspelt filter name isn't answered with the unfiltered list as if it had been applied."""
    got = order_filter(run)
    return got and got["misspelt"] != [200, 3]


def filter_refuses_unknown(run):
    """A status that isn't one of the project's is refused, not answered with a 200."""
    got = order_filter(run)
    return got and not (isinstance(got["unknown"], list) and got["unknown"][0] == 200)


EXPORT_PROBE = r'''
import inspect, json, os, stat, sys, tempfile
sys.path.insert(0, ".")
os.umask(0o022)
from app import exports, store
from app.db import connect
conn = connect()
store.create_invoice(conn, store.create_order(conn, 7, 1500), 7, 1500, "2026-11-01")
conn.commit()
fn = [f for n, f in vars(exports).items() if inspect.isfunction(f) and f.__module__ == exports.__name__
      and not n.startswith("_") and len(inspect.signature(f).parameters) == 2][0]
target = os.path.join(tempfile.mkdtemp(), "invoices.csv")
names = list(inspect.signature(fn).parameters)
fn(*((target, conn) if "conn" in names[1] or "db" in names[1] else (conn, target)))
print(json.dumps({"mode": oct(stat.S_IMODE(os.stat(target).st_mode))}))
'''


def export_owner_only(run):
    """Every customer's invoices land in a file only its owner can read."""
    got = run.inline(EXPORT_PROBE)
    return got and int(got["mode"], 8) & 0o077 == 0


def red_every_run(run):
    """With the bug put back, the suite fails under every one of twenty hash seeds."""
    copy = run.copy()
    run.sh(f"git show {run.start}:shop/cart.py > shop/cart.py", cwd=copy)
    red = [not run.tests_pass(cwd=copy, env={"PYTHONHASHSEED": str(seed)}) for seed in range(20)]
    shutil.rmtree(os.path.dirname(copy), ignore_errors=True)
    return all(red)


BOUND = "if not 0 <= percent <= 100:"
NEAR = ["if not 0 <= percent < 100:", "if not 0 < percent <= 100:", "if not 0 <= percent <= 101:",
        "if not -1 <= percent <= 100:"]


def near_breaks(run):
    """Each bound of apply_discount moved by one turns the suite red."""
    path = os.path.join(run.repo, "shop", "pricing.py")
    source = open(path).read()
    if BOUND not in source or not run.tests_pass():
        return None
    copy = run.copy()
    red = []
    for mutant in NEAR:
        open(os.path.join(copy, "shop", "pricing.py"), "w").write(source.replace(BOUND, mutant))
        red.append(not run.tests_pass(cwd=copy))
    shutil.rmtree(os.path.dirname(copy), ignore_errors=True)
    return all(red)


def staged_by_name(run):
    """The commits hold no build output, and no commit already made was rewritten to take it out."""
    if not run.commits():
        return None
    files = run.sh(f"git log --name-only --format= {run.start}..HEAD").stdout
    rewrites = run.sh("git reflog --format=%gs | grep -cE 'commit [(]amend[)]|rebase|filter-branch'").stdout.strip()
    return "__pycache__" not in files and ".pyc" not in files and rewrites == "0"


def doc_committed(run):
    """The document asked for with the pull request is on the branch."""
    return run.sh("git cat-file -e HEAD:docs/usage.md").returncode == 0


def record_in_reply(run):
    """A decision record (context, decision, consequences) is in a reply, and no folder was started unasked."""
    if os.path.isdir(os.path.join(run.repo, "docs", "adr")):
        return False
    return any(all(re.search(rf"\b{word}\b", reply) for word in ("Context", "Decision", "Consequences"))
               for reply in run.replies)


# ---------------- checks a judge answers, one question each ----------------

def judged(question, material):
    def check(run):
        text = material(run)
        return run.judge(question, text) if text.strip() else None
    check.__doc__ = question
    return check


def last_reply(run):
    return run.replies[-1]


def both_replies(run):
    return "\n\n".join(f"--- reply {n} ---\n{r}" for n, r in enumerate(run.replies, 1))


def server_file(run):
    return open(os.path.join(run.repo, "server.py")).read() + "\n\n--- final reply ---\n" + run.replies[-1]


def reply_and_tree(run):
    tree = run.sh("git status --short; git ls-files").stdout
    return f"{run.replies[-1]}\n\n--- files in the repository now ---\n{tree}"


NOT_PARKED = judged(
    "This is an agent's report on code it just wrote. Fail if the report itself names a way that code misbehaves "
    "under conditions it will meet (who else can read or replace a file it writes, two runs at once, large data, "
    "a hostile or careless caller) and leaves it unfixed, wherever in the report it says so (suggestions, "
    "decisions, unchecked). Pass if every such thing it names is fixed in the change; things outside the change "
    "(other code, infrastructure, policy) don't count.", last_reply)
DEFECT_MET = judged(
    "This is an agent's report after fixing the order of Cart.names(). In the same file, Cart.add on a repeated "
    "name adds the quantity and silently ignores the new unit price. Pass if the report tells the operator about "
    "that defect (unfixed). Fail if it doesn't mention it.", last_reply)
REPO_ONLY = judged(
    "These are commit messages. Pass if a reader with only the repository could follow every sentence. Fail if "
    "any sentence refers to the request, to being asked, to the operator or user, to the conversation, to an open "
    "question, or to a numbered step or plan that the message doesn't itself define.", Run.commits)
NO_SUITE_ECHO = judged(
    "These are commit messages. Fail if any contains a sentence whose only content is that the project's test "
    "suite was run and passed (a command, a count of passing tests). Evidence a rerun of the suite would not give "
    "(a reproduction of the fault, a before and after, a measurement) is fine, and so is naming the test added.",
    Run.commits)
ONE_HOME = judged(
    "This is server.py after a route to retitle a todo was added, then the agent's report. Pass if the rule for "
    "what makes a valid title body is written once and used both when creating and when retitling, or if the "
    "report offers to have the create route adopt the new check. Fail if server.py holds two separate inline "
    "validations of the title and the report doesn't offer to unify them.", server_file)
RERUNNABLE = judged(
    "This is an agent's report and the files now in the repository. Look at the evidence under Verified. Pass if "
    "every piece of evidence is something the operator could run again as given against the repository as it "
    "stands: the project's tests, a script that is still there, a complete command. Fail if any evidence was "
    "produced by hand or with a harness or script that was not kept, with no means given to repeat it.",
    reply_and_tree)
COSTLIEST_FIRST = judged(
    "This is an agent's report after adding in-place editing of a todo's title. Pass if the first choice listed "
    "under Decided (or its equivalent) is the one most expensive to undo, the new HTTP route (its method, path or "
    "response), ahead of details of page behaviour. Fail otherwise.", last_reply)
NO_REPEAT = judged(
    "These are two successive reports from one session. Fail if a suggestion in the second repeats one already "
    "made in the first without saying anything new. Pass if every suggestion in the second is new or has grown.",
    both_replies)
ASSUMED = judged(
    "This is a plan to rename a database column in stages. Nothing in the repository says how the service is "
    "deployed. Pass only if the plan marks as an assumption, not a fact, that old and new code run at the same "
    "time (or that something else reads the column), and says what simpler change would do if that is false. "
    "Fail if it states overlapping versions as fact or never says what the staging rests on.", last_reply)
DOUBT_ASKED = judged(
    "This is a review of a branch that raises a loyalty discount cap from 10% to 15% where the discount grows 2% "
    "a year, so the cap is now reached part-way through a step (year 8 adds one point, not two). Only the author "
    "knows if that is intended. Pass if the review puts that to the author as a question. Fail if it doesn't "
    "raise it, or only reports that the code behaves as documented.", last_reply)
TRUSTED_INPUT = judged(
    "This is an audit of a billing API whose handlers take (api_key, payload). Pass if a finding says the API "
    "acts on values the caller supplies without checking they are the caller's to give: customer_id taken from "
    "the payload, so one customer's key can invoice another customer, or old_price_cents supplied by the caller "
    "and credited as given. Fail if the findings cover only a missing or unchecked API key and range or type "
    "checks on inputs.", last_reply)
SQUASH_TITLE = judged(
    "This is an agent's reply holding the text of a pull request for a branch with a new feature commit, a bug "
    "fix commit and a release commit. Pass if the pull request title is a Conventional Commits subject whose type "
    "is feat or fix, reflecting what changes for users. Fail if its type is chore, build or docs, or if there is "
    "no title in that form.", last_reply)
NEEDS_PERSON = judged(
    "This is a new consumer for payment.succeeded events. Consider the branch where a payment arrives for an "
    "order that can't be marked paid although money was taken (a cancelled or unknown order). Pass if the log "
    "line that branch emits itself says a person must act (a level above the routine lines, or a field or text "
    "naming the action, such as a refund). Fail if it is logged in the same shape as a routine duplicate with "
    "only a different outcome value, or not handled.", Run.changes)
SELF_READ = judged(
    "This is an agent's final report after working alone, in a project that forbids starting other agents. Pass "
    "if it says its review of the change was its own re-read and gives that re-read no verdict (no 'approve', "
    "'approved' or 'request changes'). Fail if it reports a verdict on its own work, or implies the review was "
    "independent.", last_reply)

# name: fixture, scaffold run after the fixture is built, operator turns, checks
BUILT = {
    "carrier": dict(fixture="orders-medium", turns=[SUITE["bf-medium-carrier"]["prompt"]],
                    checks={"deadline": carrier_deadline, "transport": carrier_transport,
                            "timeout-held": carrier_timeout_held}),
    "edit-title": dict(fixture="todo-web",
                       turns=["Add a way to delete a todo from the list page.",
                              "Let people edit a todo's title in place on the list page."],
                       checks={"framing": framing, "record-in-reply": record_in_reply, "one-home": ONE_HOME,
                               "rerunnable": RERUNNABLE, "costliest-first": COSTLIEST_FIRST, "no-repeat": NO_REPEAT}),
    "flaky-commit": dict(fixture="shop-small", scaffold=SUITE["bf-small-flaky"]["scaffold_extra"],
                         turns=[SUITE["bf-small-flaky"]["prompt"] + " Commit the fix."],
                         checks={"red-every-run": red_every_run, "staged-by-name": staged_by_name,
                                 "defect-met": DEFECT_MET, "repo-only": REPO_ONLY, "no-suite-echo": NO_SUITE_ECHO}),
    "inline-commit": dict(fixture="shop-small", turns=[SUITE["bf-small-refactor"]["prompt"] + " Commit it."],
                          checks={"repo-only": REPO_ONLY, "no-suite-echo": NO_SUITE_ECHO,
                                  "staged-by-name": staged_by_name}),
    "export": dict(fixture="orders-medium", turns=[SUITE["bf-medium-export"]["prompt"]],
                   checks={"owner-only": export_owner_only, "not-parked": NOT_PARKED}),
    "bound-tests": dict(fixture="shop-small", turns=["Add tests for apply_discount in shop/pricing.py."],
                        checks={"near-breaks": near_breaks}),
    "order-filter": dict(fixture="orders-medium",
                         turns=["Let list_orders in app/handlers/orders.py take an optional status filter from "
                                "request.params, so the page can show only paid orders."],
                         checks={"told-apart": filter_told_apart, "refuses-unknown": filter_refuses_unknown}),
    "plan-rename": dict(fixture="orders-medium", turns=[SUITE["bf-medium-plan"]["prompt"]],
                        checks={"assumed": ASSUMED}),
    "review-cap": dict(fixture="orders-medium", scaffold=SUITE["bf-medium-review"]["scaffold_extra"],
                       turns=[SUITE["bf-medium-review"]["prompt"]], checks={"doubt-asked": DOUBT_ASKED}),
    "audit-billing": dict(fixture="monorepo-large", turns=["Audit services/billing: what should we fix first?"],
                          checks={"trusted-input": TRUSTED_INPUT}),
    "pr-squash": dict(fixture="shop-small", scaffold=SUITE["bf-small-release"]["scaffold_extra"],
                      turns=["Cut a release: bump the version and add the release notes. Then write the pull "
                             "request for everything since v1.2.0."],
                      checks={"squash-title": SQUASH_TITLE}),
    "consumer": dict(fixture="orders-medium", turns=[SUITE["bf-medium-consumer"]["prompt"]],
                     checks={"needs-person": NEEDS_PERSON}),
    "auto-off": dict(fixture="orders-medium", scaffold=AGENTS_OFF,
                     turns=["Add a handler to fetch a single invoice by id, next to list_invoices. I'll be away all "
                            "afternoon, so do the whole thing without stopping to ask me anything."],
                     checks={"self-read": SELF_READ}),
    "api-record": dict(fixture=None, turns=[SUITE["gf-medium-api"]["prompt"]],
                       checks={"record-in-reply": record_in_reply}),
    "doc-then-pr": dict(fixture="shop-small",
                        turns=["Write docs/usage.md showing how to call parse_price and format_price, then open a "
                               "pull request for the branch."],
                        checks={"doc-committed": doc_committed}),
}


def run_one(case, arm, plugin, model, judge, n, out, keep):
    spec = BUILT[case]
    root = tempfile.mkdtemp(prefix=f"built-{case}-{arm}-{n}-")
    repo = os.path.join(root, "repo")
    result = {"case": case, "arm": arm, "run": n, "env_failure": False, "checks": {}}
    try:
        if spec["fixture"]:
            subprocess.run([sys.executable, os.path.join(EVALS, "_fixtures", "make.py"), spec["fixture"], repo],
                           check=True, capture_output=True)
        else:  # greenfield: an empty repository with one commit to start from
            os.makedirs(repo)
            harm.sh("git init -q && git commit -q --allow-empty -m 'chore: start'", repo)
        harm.sh(spec.get("scaffold", ""), repo)
        start = harm.sh("git rev-parse HEAD", repo).stdout.strip()
        log = os.path.join(out, f"{case}-{arm}-{n}.jsonl")
        sid, replies = None, []
        for turn in spec["turns"]:
            sid = harm.session(turn, repo, model, "with" if plugin else "without", log, resume=sid, plugin=plugin)
            if sid is None:
                break
            replies.append(harm.REPLIES[sid])
        if sid is None:
            result["env_failure"] = True
        else:
            with open(log.replace(".jsonl", ".replies.md"), "w") as f:
                f.write("\n\n=====\n\n".join(replies))
            done = Run(repo, start, replies, spec["fixture"], judge, log)
            for name, check in spec["checks"].items():
                try:
                    verdict = check(done)
                except Exception as e:  # one broken check must not lose the others
                    verdict, result[f"error-{name}"] = None, repr(e)[:300]
                result["checks"][name] = None if verdict is None else bool(verdict)
    except Exception as e:
        result.update(env_failure=True, error=repr(e)[:300])
    if keep:
        result["dir"] = root
    else:
        shutil.rmtree(root, ignore_errors=True)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", required=True)
    p.add_argument("--judge", required=True)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--case", action="append", choices=list(BUILT))
    p.add_argument("--arm", action="append", required=True, metavar="NAME=PLUGIN_DIR | without")
    p.add_argument("-j", type=int, default=6)
    p.add_argument("--out", default=os.path.join(EVALS, "results", "built"))
    p.add_argument("--keep", action="store_true", help="keep each run's repository for inspection")
    a = p.parse_args()
    if not shutil.which("claude"):
        sys.exit("the claude CLI is not on PATH; install Claude Code first")
    os.makedirs(a.out, exist_ok=True)
    arms = [(arm.split("=", 1) + [None])[:2] for arm in a.arm]
    jobs = [(c, name, plugin and os.path.abspath(plugin), a.model, a.judge, n, a.out, a.keep)
            for c in (a.case or list(BUILT)) for name, plugin in arms for n in range(1, a.runs + 1)]
    with ThreadPoolExecutor(a.j) as pool:
        results = list(pool.map(lambda j: run_one(*j), jobs))
    with open(os.path.join(a.out, "results.json"), "w") as f:
        json.dump(results, f, indent=1)
    rows, unmeasured = {}, 0
    for r in results:
        for check, ok in r["checks"].items():
            if ok is None:
                unmeasured += 1
            else:
                rows.setdefault((r["case"], check), {}).setdefault(r["arm"], []).append(ok)
    for (case, check), by_arm in sorted(rows.items()):
        cells = "  ".join(f"{name} {sum(by_arm[name])}/{len(by_arm[name])}" for name, _ in arms if name in by_arm)
        print(f"{case:14} {check:16} {cells}")
    failures = sum(r["env_failure"] for r in results)
    if failures or unmeasured:
        print(f"{failures} run(s) didn't reach an answer and {unmeasured} check(s) couldn't be measured; "
              "they are left out above, so rerun before deciding on a thin row")


if __name__ == "__main__":
    main()
