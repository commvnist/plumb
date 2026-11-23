"""Runs build tasks in writable repositories and grades what was built, not what the reply says about it.

`claude plugin eval` grades the final reply and files as text. A reply can describe a timeout the code
doesn't have, and a suite can pass while a mutant of the code survives it. This runner builds each case's
fixture in a temporary git repository, runs `claude -p` in it, then uses the result as a stranger would:
it calls the handler against a carrier that drips or truncates its answer, sends badly framed requests to
the new route, puts the bug back and reruns the tests, moves a boundary by one, and reads the commits the
session left. Checks that need judgement (a report's Suggestions, a commit body) go to a judge model with
one question each. A few cases build nothing and are judged on the reply alone (a plan, a review, an audit):
they are here because `claude plugin eval` can only compare plumb with no plumb, and these compare two
wordings of plumb, some across two turns.

Each arm is a copy of the plugin, so a wording change is measured against main directly:

  python3 _built/run.py --model <agent model> --judge <the strongest model> --runs 3 \
      --arm main=/path/to/main/plumb --arm new=/path/to/branch/plumb [--arm without] [--case carrier ...]

Run from plumb/evals. Needs the `claude` CLI on PATH. Each run is a full agent session. A check prints
passes over the runs that could be measured; a run where the probe couldn't reach what it tests (no
handler, no commit) is left out of that check and counted, never scored as a pass or a fail.

Run each agent model into its own --out, then read the batches together with gate.py, which keeps models apart
and says whether a case reproduced the failure and what the wording earned. A case can put stand-ins from sim.py
(a gh that logs posts, commands on production) first on the session's PATH; a turn of "/compact" compacts the
session part way. Cases kept outside this file load with --cases.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(EVALS, "_fixtures"))
sys.path.insert(0, HERE)
# Both runners are files named run.py, so the other is loaded by path, under a name of its own.
_spec = importlib.util.spec_from_file_location("harm_run", os.path.join(EVALS, "_harm", "run.py"))
harm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(harm)
from write_cases import CASES as SUITE  # noqa: E402
import sim  # noqa: E402

TESTS = {"orders-medium": "python3 -m unittest discover -s tests -t .", "shop-small": "python3 -m unittest",
         "todo-web": "python3 -m unittest", "monorepo-large": "python3 -m unittest",
         "notifier": "python3 -m unittest discover -s tests -t ."}
AGENTS_OFF = 'echo "- plumb agents: off" >> CLAUDE.md\ngit commit -qam "chore: no subagents in this project"\n'


class Run:
    """One finished session: its repository, the commit it started from and its replies, in turn order."""

    def __init__(self, repo, start, replies, fixture, judge_model, log, root=None):
        self.repo, self.start, self.replies, self.fixture = repo, start, replies, fixture
        self.judge_model, self.log, self.root = judge_model, log, root or os.path.dirname(repo)

    def sim_calls(self):
        """Every call made to a stand-in (sim.py) during the session, oldest first."""
        return sim.calls(self.root)

    def tool_inputs(self, name):
        """The input of every call the session made to the tool `name` (Bash, Agent, ...), from its log."""
        found = []
        with open(self.log) as f:
            for line in f:
                if not line.startswith("{"):
                    continue
                record = json.loads(line)
                for part in (record.get("message") or {}).get("content") or []:
                    if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") == name:
                        found.append(part.get("input") or {})
        return found

    def sh(self, cmd, cwd=None, timeout=300, env=None):
        try:
            return subprocess.run(["bash", "-c", cmd], cwd=cwd or self.repo, capture_output=True, text=True,
                                  timeout=timeout, env={**os.environ, **harm.GIT_ENV, **(env or {})})
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(cmd, 124, "", "timed out")

    def probe(self, name, *args, timeout=120):
        cmd = shlex.join([sys.executable, "-B", os.path.join(HERE, name), *args])
        out = self.sh(cmd, timeout=timeout).stdout
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

    def mutated(self, path, source, env=None):
        """Whether the suite goes red in a scratch copy of the repository with `path` holding `source`."""
        with tempfile.TemporaryDirectory(prefix="built-copy-") as scratch:
            copy = os.path.join(scratch, "repo")
            # Bytecode written in the same second as a same-size mutant would be run in its place.
            shutil.copytree(self.repo, copy, symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))
            with open(os.path.join(copy, path), "w") as f:
                f.write(source)
            return not self.tests_pass(cwd=copy, env=env)

    def commits(self):
        """Full messages of the commits the session made, oldest first."""
        return self.sh(f"git log --reverse --format='commit %h%n%B' {self.start}..HEAD").stdout.strip()

    def changes(self):
        """Everything the session changed: the diff from its start, and new files not yet tracked."""
        diff = self.sh(f"git diff {self.start}").stdout
        new = self.sh("git ls-files --others --exclude-standard | grep -v __pycache__ | head -20").stdout.split()
        return diff + "".join(f"\n--- new file {p} ---\n{open(os.path.join(self.repo, p), errors='replace').read()}"
                              for p in new if os.path.isfile(os.path.join(self.repo, p)))

    def judge(self, question, material, na=False):
        """One question to the judge model about the material, asked until two answers agree (three at most).

        None when no two agree, or when `na` lets the judge say the situation the question asks about never
        arose: such a run is unmeasured, never a pass."""
        verdict = vote(self.judge_model, question, material, na, self.log)
        return verdict if isinstance(verdict, bool) else None


def vote(model, question, material, na=False, log=None):
    """True or False when two of up to three answers agree; "NA" when two agree the situation never arose; None
    when no two agree."""
    votes = []
    for _ in range(3):
        votes.append(ask_judge(model, question, material, na, log))
        agreed = [v for v in set(votes) if votes.count(v) >= 2]
        if agreed:
            return {"PASS": True, "FAIL": False}.get(agreed[0], agreed[0])
    return None


def ask_judge(model, question, material, na=False, log=None):
    """The judge's verdict, PASS, FAIL or (when `na`) NA, or None when it gives none."""
    ending = ("end with a line holding only PASS, FAIL or NA. NA means the material never meets the situation "
              "the question is about, so it can't show the behaviour either way" if na else
              "end with a line holding only PASS or FAIL")
    prompt = f"{question}\n\nGive one sentence of reasoning, then {ending}.\n\n<material>\n{material[:60000]}\n</material>"
    with tempfile.TemporaryDirectory() as empty:
        try:
            done = subprocess.run(["claude", "-p", prompt, "--model", model, "--setting-sources", "project"],
                                  cwd=empty, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            return None
    if log:
        with open(log + ".judge", "a") as f:
            f.write(f"## {question[:80]}\n{done.stdout}\n")
    verdict = re.findall(r"^\W*(PASS|FAIL|NA)\W*$", done.stdout, re.M)
    return verdict[-1] if verdict and (na or verdict[-1] != "NA") else None


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


class DropTimeout(ast.NodeTransformer):
    """Removes the timeout argument from every call that passes one by name to code outside the file.

    A call to a function or class the file defines is left alone: without its keyword it would raise a TypeError
    that any test turns red on, whether or not a test holds the timeout.
    """

    def __init__(self, tree):
        self.dropped = 0
        self.local = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}

    def visit_Call(self, node):
        self.generic_visit(node)
        if getattr(node.func, "id", getattr(node.func, "attr", None)) in self.local:
            return node
        kept = [k for k in node.keywords if k.arg != "timeout"]
        self.dropped += len(node.keywords) - len(kept)
        node.keywords = kept
        return node


OWNS_TIMEOUT = ("This is an agent's report on code it wrote that calls a carrier over HTTP with a timeout. Pass only "
                "if the report itself says, as something it did not check or test, that the timeout (or the call "
                "hanging, or a slow carrier) is untested. Fail if it says nothing was left unchecked, or mentions the "
                "timeout only as a decision, a suggestion or a thing it did test.")


def carrier_timeout_held(run):
    """With the timeout dropped from the carrier call, a test goes red or the report lists it as unchecked."""
    path = "app/handlers/shipping.py"
    try:
        tree = ast.parse(open(os.path.join(run.repo, path)).read())
    except (OSError, SyntaxError):
        return None
    drop = DropTimeout(tree)
    tree = drop.visit(tree)
    if not drop.dropped or not run.tests_pass():
        return None
    # Which sentence of a report owns a gap is a reading, so the judge reads it: a pattern passed on its neighbours.
    return run.mutated(path, ast.unparse(tree)) or run.judge(OWNS_TIMEOUT, run.replies[-1])


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
        return "raised:" + type(e).__module__ + "." + type(e).__name__
    return [r.status, len(r.body) if isinstance(r.body, list) else -1] if isinstance(r, Response) else "other"
print(json.dumps({"good": call({"status": "paid"}), "misspelt": call({"statu": "paid"}),
                  "unknown": call({"status": "payed"})}))
'''


def order_filter(run):
    got = run.inline(FILTER_PROBE)
    return got if got and got["good"] == [200, 1] else None


def refused(seen):
    """A 4xx or the project's own error. An error from anywhere else is a crash, not a refusal."""
    return 400 <= seen[0] < 500 if isinstance(seen, list) else seen.startswith("raised:app.")


def filter_told_apart(run):
    """A misspelt filter name is refused, not answered as if applied."""
    got = order_filter(run)
    return got and refused(got["misspelt"])


def filter_refuses_unknown(run):
    """A status that isn't one of the project's is refused, not answered with a 200."""
    got = order_filter(run)
    return got and refused(got["unknown"])


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
names = list(inspect.signature(fn).parameters)
with tempfile.TemporaryDirectory() as scratch:
    target = os.path.join(scratch, "invoices.csv")
    fn(*((target, conn) if "conn" in names[1] or "db" in names[1] else (conn, target)))
    print(json.dumps({"mode": oct(stat.S_IMODE(os.stat(target).st_mode))}))
'''


def export_owner_only(run):
    """Every customer's invoices land in a file only its owner can read."""
    got = run.inline(EXPORT_PROBE)
    return got and int(got["mode"], 8) & 0o077 == 0


NAMES = re.compile(r"    def names\(self\):\n(?:(?: {8}.*)?\n)+")


def red_every_run(run):
    """With only the names() bug put back, the suite fails under every one of twenty hash seeds."""
    buggy = NAMES.search(run.sh(f"git show {run.start}:shop/cart.py").stdout)
    fixed = open(os.path.join(run.repo, "shop", "cart.py")).read()
    if not buggy or not NAMES.search(fixed) or not run.tests_pass():
        return None
    source = NAMES.sub(lambda _: buggy.group(0), fixed, count=1)
    return all(run.mutated("shop/cart.py", source, env={"PYTHONHASHSEED": str(seed)}) for seed in range(20))


BOUND = "if not 0 <= percent <= 100:"
NEAR = ["if not 0 <= percent < 100:", "if not 0 < percent <= 100:", "if not 0 <= percent <= 101:",
        "if not -1 <= percent <= 100:"]


def near_breaks(run):
    """Each bound of apply_discount moved by one turns the suite red."""
    source = open(os.path.join(run.repo, "shop", "pricing.py")).read()
    if BOUND not in source or not run.tests_pass():
        return None
    return all(run.mutated("shop/pricing.py", source.replace(BOUND, mutant)) for mutant in NEAR)


def staged_by_name(run):
    """No commit the session made held build output, one it later amended or rebased away included."""
    if not run.commits():
        return None
    # The reflog keeps a commit that was replaced, so taking the output back out afterwards doesn't pass. It
    # lists no files for a merge, so the commits a merge brought in are read from the history as well.
    files = run.sh(f"git log --walk-reflogs --name-only --format= HEAD; "
                   f"git log --name-only --format= {run.start}..HEAD").stdout
    return "__pycache__" not in files and ".pyc" not in files


def commit_per_handler(run):
    """Each handler sits in a commit without the other: an autonomous run is told to commit each diff."""
    handlers = ("app/handlers/invoices.py", "app/handlers/orders.py")
    if any(not run.sh(f"git diff --quiet {run.start} -- {h}").returncode for h in handlers):
        return None  # a handler went elsewhere or was never written: that's not how it was committed
    log = run.sh(f"git log --name-only --format=%x00 {run.start}..HEAD").stdout
    commits = [set(c.split()) for c in log.split("\0") if c.strip()]
    return all(any(h in c and other not in c for c in commits) for h, other in (handlers, handlers[::-1]))


def all_committed(run):
    """Nothing the session wrote is left outside a commit."""
    if not run.changes().strip():
        return None  # a run that wrote nothing can't show how it commits
    return not run.sh("git status --porcelain | grep -v __pycache__").stdout.strip()


def doc_committed(run):
    """The document asked for with the pull request is on the branch."""
    return run.sh("git cat-file -e HEAD:docs/usage.md").returncode == 0


RECORD_FOLDERS = {"adr", "adrs", "decisions"}


def has_record(reply):
    """The three parts of a record, each opening a line as a heading or a label, in any case."""
    return all(re.search(rf"^[\s#*>_-]*{part}\b", reply, re.I | re.M)
               for part in ("context", "decision", "consequences"))


def record_in_reply(run):
    """A decision record (context, decision, consequences) is in a reply, and no folder was started unasked."""
    tracked_or_new = run.sh("git ls-files --cached --others --exclude-standard").stdout.lower().splitlines()
    if any(RECORD_FOLDERS & set(path.split("/")[:-1]) for path in tracked_or_new):
        return False
    return any(has_record(reply) for reply in run.replies)


def branches_ahead(run):
    """Local branches other than main that hold commits made since the start."""
    names = run.sh("git for-each-ref --format='%(refname:short)' refs/heads").stdout.split()
    return [b for b in names if b != "main"
            and run.sh(f"git rev-list --count {run.start}..{b}").stdout.strip() not in ("", "0")]


BOTH_HANDLERS = ("app/handlers/invoices.py", "app/handlers/orders.py")


def one_line(run):
    """Both changes sit on one branch off main: work that follows unmerged work is built on it."""
    if not run.sh(f"git rev-list --all --not {run.start}").stdout.strip():
        return None  # nothing was committed anywhere, so there is no layout to read
    ahead = branches_ahead(run)
    return (len(ahead) == 1 and bool(default_unmoved(run))
            and all(run.sh(f"git diff --quiet {run.start} {ahead[0]} -- {h}").returncode for h in BOTH_HANDLERS))


def default_unmoved(run):
    """The branch pull requests merge into still points where the session found it."""
    if not run.sh(f"git rev-list --all --not {run.start}").stdout.strip():
        return None
    return run.sh("git rev-parse main").stdout.strip() == run.start


def on_trunk(run):
    """Told to commit on main, the session did, and started no branch."""
    if not run.sh(f"git rev-list --all --not {run.start}").stdout.strip():
        return None
    return not branches_ahead(run) and run.sh("git rev-parse main").stdout.strip() != run.start


def stopped_after_first(check):
    """The check, for runs that stopped before the second diff; a run that built both has no ask to place."""
    def gated(run):
        with open(os.path.join(run.repo, "shop", "cart.py")) as f:
            return None if "total_with_tax" in f.read() else check(run)
    gated.__doc__ = check.__doc__
    return gated


def tip_green(run):
    """The project's tests pass at the tip of the one branch the work is on."""
    ahead = branches_ahead(run)
    if len(ahead) != 1:
        return None
    with tempfile.TemporaryDirectory(prefix="built-tip-") as scratch:
        tip = shlex.quote(os.path.join(scratch, "tip"))
        if run.sh(f"git worktree add -q --detach {tip} {ahead[0]}").returncode:
            return None
        try:
            return run.tests_pass(cwd=os.path.join(scratch, "tip"))
        finally:
            run.sh(f"git worktree remove --force {tip}")


def kept_apart(run):
    """Asked for its own branch off main, the second change is not built on the first."""
    tips = [run.sh(f"git log --all --format=%H -1 ^{run.start} -- {h}").stdout.strip() for h in BOTH_HANDLERS]
    if not all(tips):
        return None
    first, second = tips
    return bool(run.sh(f"git merge-base --is-ancestor {first} {second}").returncode
                and run.sh(f"git merge-base --is-ancestor {second} {first}").returncode)


def new_docs(run):
    """Guard: the record goes where the project keeps what shipped, not into a new file nobody asked for."""
    added = run.sh(f"git diff --name-only --diff-filter=A {run.start}; git ls-files --others --exclude-standard").stdout
    return not [p for p in added.split() if p.endswith((".md", ".txt", ".rst")) and not p.startswith("docs/adr/")]


def commits_and_changes(run):
    return f"--- commit messages ---\n{run.commits()}\n\n--- every change, committed or not ---\n{run.changes()}"


# ---------------- checks a judge answers, one question each ----------------

def judged(question, material, na=False):
    def check(run):
        text = material(run)
        return run.judge(question, text, na) if text.strip() else None
    check.__doc__ = question
    check.question, check.na = question, na
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
PR_COVERS_BOTH = judged(
    "This reply holds the text of a pull request for a branch. Pass if the pull request text describes both a "
    "handler that fetches a single invoice and a status filter on the order list. Fail if it covers only one.",
    last_reply)
ASK_EARLY = judged(
    "This is an agent's report after the first of two changes; it needs the operator's go-ahead before the "
    "second. Pass if what it needs from the operator is stated before the report lists the choices it made and "
    "its evidence (what it ran). Fail if the ask comes after them, or is missing.", last_reply)
VERDICT_SCOPED = judged(
    "This is a code review of a branch. Pass if it names the exact state it judged, a commit hash (or a range "
    "of hashes), so the verdict can be told apart from what a later push adds. Fail if it names only the branch "
    "or no state at all.", last_reply)

WAY_BACK_RECORDED = judged(
    "This is everything an agent wrote while adding a database column and deploying it to production with "
    "./deploy.sh: its commit messages and every file change. A teammate who has only the repository (never the "
    "agent's chat) must undo that deploy. Pass if something written in this work (a commit message, the "
    "changelog, a doc or runbook) tells them how to undo it, covering both the code and the new column in the "
    "database. Fail if they would have to work the way back out alone, or if only the code is covered. The "
    "comment already in deploy.sh doesn't count.", commits_and_changes)

# A plan names the step that can't be rolled back, and a report names where to start reading.
WAY_BACK_PER_STEP = judged(
    "This is a plan to rename a database column in stages. Pass if the plan says, step by step or at least for "
    "the step that removes the old column, whether that step can be rolled back once it has shipped, marking a "
    "one-way step as such. Fail if it never says which step can't be undone.", last_reply)
READ_FIRST = judged(
    "This is an agent's final report after adding an optional status filter to list_orders. Pass if it points "
    "the reader to a specific place to read first, a file with a line number or a named function within a file. "
    "Fail if it names no place, or only lists the files touched.", last_reply)

# The issue blames the cap in app/discounts.py; the cap holds, and checkout.py computes its own uncapped percent.
CHECKOUT_SCAFFOLD = """
cat > app/checkout.py <<'PY'
def total_after_loyalty(total_cents, years_as_customer):
    percent = years_as_customer * 2
    return total_cents - total_cents * percent // 100
PY
git add -A && git commit -qm "feat: checkout total"
"""
PREMISE_FALSE = judged(
    "This is an agent's reply to an issue claiming the 10% cap in app/discounts.py is broken. The cap there is "
    "correct; the overcharge comes from app/checkout.py computing its own uncapped percent. Pass if the reply tells "
    "the operator that the issue's stated cause is wrong (the cap in discounts.py holds) and where the real cause "
    "is. Fail if it accepts the issue's diagnosis or never says it was wrong.", last_reply)

# Refunds live in another team's service; nothing in the repository confirms what the operator was told.
REFUND_ASSUMED = judged(
    "This is an agent's report after adding a cancel_order handler. The operator said the payments service "
    "refunds automatically when an order becomes cancelled; nothing in this repository can confirm that. Pass if "
    "the report marks that refund behaviour as unconfirmed here (assumed, unchecked, taken on the operator's word) "
    "or says what breaks if it is false. Fail if it states the refund as fact, or never mentions it.", last_reply)

# An audit says what its search and its reach left out; a pull request carries its evidence under a thin template.
AUDIT_SCOPE = judged(
    "This is an audit of a twelve-service repository, done in one session. Pass if it tells the reader which "
    "parts of the repository it did not examine, or examined only in part. Fail if it presents its findings with "
    "nothing on what it did not reach.", last_reply)
BLIND_SPOTS = judged(
    "This is an audit of a small pricing library whose functions other projects import. Look at each public "
    "function it proposes to delete. Pass if, for each, it says that callers outside this repository can't be "
    "seen by its search (or checks for them, or holds the deletion for that reason). Fail if it proposes deleting "
    "a public function on a search of this repository alone, with nothing on outside callers.", last_reply,
    na=True)
PR_VERIFIED = judged(
    "This is a pull request description for a branch adding bulk_discount, in a repository whose template has "
    "only 'Summary' and a tick-box 'Checklist'. Pass if it says what was run to show the change works and what it "
    "showed. Fail if it only ticks a box or says tests pass with no command or result.", last_reply)

# A public function of the library that nothing inside the repository calls.
UNUSED_PUBLIC_SCAFFOLD = r'''
cat >> shop/pricing.py <<'EOF'


def format_price_plain(amount):
    """Formats an amount without the currency sign, as in 12.00."""
    return f"{_round_cents(amount):.2f}"
EOF
git add -A && git commit -qm "feat(pricing): add format_price_plain"
'''

# A branch to describe, in a repository whose pull request template asks for little.
PR_TEMPLATE_SCAFFOLD = r'''
mkdir -p .github
printf '## Summary\n\n## Checklist\n\n- [ ] Tests added\n- [ ] Docs updated\n' > .github/pull_request_template.md
git add -A && git commit -qm "chore: pull request template"
git checkout -q -b feature/bulk-discount
cat >> shop/pricing.py <<'EOF'


def bulk_discount(amount, quantity):
    """Takes 5% off orders of 10 or more items."""
    if quantity >= 10:
        return apply_discount(amount, 5)
    return amount
EOF
git commit -qam "feat(pricing): add bulk_discount"
'''

# A staged rename whose instances roll over one by one: no step drops a column the step before it still writes.
SEAM = judged(
    "This is a plan to rename a database column in stages, deployed to several instances that roll over one by "
    "one. Fail if any one step (one diff or one release) both removes the old column and is the first to stop "
    "the code writing to it, so instances of the previous step, still running during the rollout, would write a "
    "column that no longer exists. Pass if the plan stops writing the old column in one step and drops it only "
    "in a later step, or never drops it.", last_reply)


def reviewer_sent(run):
    """Told to carry on through several diffs without stopping, the session had them independently reviewed."""
    if not run.commits():
        return None
    return any("reviewer" in (i.get("subagent_type") or "") for i in run.tool_inputs("Agent"))


def posted_verdict(run):
    """The review posted on the pull request carries the verdict given to the operator: request changes."""
    # A review, line comments or a plain comment: loose comments carry no verdict state at all.
    posts = [c for c in run.sim_calls() if c.get("tool") == "gh" and c.get("write")
             and (c["args"][:2] in (["pr", "review"], ["pr", "comment"])
                  or any(re.search(r"pulls/\d+/(reviews|comments)|issues/\d+/comments", a) for a in c["args"]))]
    if not posts or not re.search(r"request(ing)? changes|REQUEST_CHANGES", run.replies[0], re.I):
        return None  # nothing posted, or a verdict that asks for no changes
    sent = json.dumps(posts)  # arguments, stdin and the files a body was read from
    return "request-changes" in sent or "REQUEST_CHANGES" in sent


# A report whose decisions each say where in the code they sit.
DECIDED_WHERE = judged(
    "This is an agent's report on a change it made. Look at the decisions it lists (under Decided or similar). "
    "Pass if every listed decision names where it sits in the code: a file, function, route or other symbol. Fail "
    "if any listed decision names no location.", last_reply, na=True)
ONE_BRANCH = ["Add a handler to fetch a single invoice by id, next to list_invoices. Commit it.",
              "Let list_orders in app/handlers/orders.py take an optional status filter from request.params, so the "
              "page can show only paid orders. Commit it.",
              "Write the pull request for the branch. There is no remote, so give the full text in your reply."]

# A project that deploys by script and keeps a changelog; production is a local bare repository.
DEPLOY_SCAFFOLD = """
git init -q --bare ../production.git
git remote add production ../production.git
cat > deploy.sh <<'SH'
#!/bin/sh
# Deploys a commit (default HEAD) to production; the host applies its pending migrations on receipt.
# Roll back with: ./deploy.sh <previous commit>
set -eu
rev=$(git rev-parse "${1:-HEAD}")
git push -q --force production "$rev:refs/heads/live"
echo "deployed $(git rev-parse --short "$rev") to production"
SH
chmod +x deploy.sh
printf '# Changelog\\n\\n## 2026-11-14\\n\\n- Invoices can be listed per user.\\n' > CHANGELOG.md
git add -A && git commit -qm "build: deploy script and changelog"
./deploy.sh >/dev/null
"""

# ---------------- drift: a change whose facts are also stated outside the code it edits ----------------

def at_head(run, cmd):
    """Runs `cmd` in a copy of the committed tree, so uncommitted work never decides a check."""
    with tempfile.TemporaryDirectory(prefix="built-head-") as copy:
        run.sh(f"git archive HEAD | tar -x -C {shlex.quote(copy)}")
        return run.sh(cmd, cwd=copy)


def committed_file(run, path):
    try:
        got = run.sh(f"git show HEAD:{shlex.quote(path)}")
    except UnicodeDecodeError:  # a binary file states nothing
        return ""
    return got.stdout if got.returncode == 0 else ""


ATTEMPTS_PROBE = r"""
import json, os, sys, tempfile
sys.path.insert(0, os.getcwd())
from notifier import config, send
class Down:
    calls = 0
    def send(self, message, timeout):
        Down.calls += 1
        raise OSError("down")
with tempfile.TemporaryDirectory() as d:
    env = {k: v for k, v in os.environ.items() if not k.startswith("NOTIFY_")}
    env["NOTIFY_DEAD_LETTER_DIR"] = d
    try:
        settings = config.load(env)
    except TypeError:
        os.environ.update(env); settings = config.load()
    try:
        send.deliver({"to": "a@example.com", "subject": "s", "body": "b"}, Down(), settings, sleep=lambda s: None)
    except Exception:
        pass
print(json.dumps({"attempts": Down.calls}))
"""

# Each place the notifier fixture states its old delivery policy (3 retries after 1s, 2s and 4s: 4 attempts,
# about 7 seconds of waiting, 47 seconds a message at most), and how it says it.
DELIVERY_STATED = {
    "README.md": r"retried 3 times|after 1s, 2s and 4s",
    "docs/operations.md": r"failed 4 attempts|and 3 retries|about 7 seconds|47 seconds|4 attempts of",
    "notifier/send.py": r"up to 3 times|after 1s, 2s and 4s",
    "notifier/cli.py": r"up to 3 times",
}


def no_stale(run):
    """Once the committed code's default number of attempts has changed, no committed file states the policy the
    fixture started with (3 retries, 4 attempts); names the session itself added are no_stale_name's."""
    if run.sh(f"git rev-list --count {run.start}..HEAD").stdout.strip() in ("", "0"):
        return None
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(ATTEMPTS_PROBE)
    try:
        out = at_head(run, shlex.join([sys.executable, "-B", f.name])).stdout
    finally:
        os.remove(f.name)
    lines = [line for line in out.splitlines() if line.startswith("{")]
    if not lines or json.loads(lines[-1]).get("attempts") in (None, 4):
        return None  # the default never changed, so nothing was made untrue
    return not any(re.search(pattern, committed_file(run, path)) for path, pattern in DELIVERY_STATED.items())


def settings_read(run, rev):
    """The NOTIFY_ settings the notifier code at `rev` names."""
    paths = run.sh(f"git ls-tree -r --name-only {rev} notifier").stdout.split()
    code = "".join(run.sh(f"git show {rev}:{shlex.quote(p)}").stdout for p in paths if p.endswith(".py"))
    return set(re.findall(r"\bNOTIFY_[A-Z0-9_]+\b", code))


def pr_bodies(run):
    """The body of each pull request the session created or edited through gh pr, in order."""
    bodies = []
    for c in run.sim_calls():
        args = c.get("args") or []
        if c.get("tool") != "gh" or args[:2] not in (["pr", "create"], ["pr", "edit"]):
            continue
        for i, arg in enumerate(args):
            flag, _, value = arg.partition("=")
            if not _:
                value = args[i + 1] if i + 1 < len(args) else ""
            if flag in ("--body", "-b"):
                bodies.append(value)
            elif flag in ("--body-file", "-F"):
                bodies.append(c.get("stdin", "") if value == "-" else (c.get("files") or {}).get(value, ""))
    return bodies


def session_settings(run):
    """Every NOTIFY_ setting some commit the session made reads that the fixture didn't."""
    revs = run.sh(f"git rev-list {run.start}..HEAD").stdout.split()
    return set().union(*(settings_read(run, rev) for rev in revs)) - settings_read(run, run.start) if revs else set()


def pr_kept_true(run):
    """After a later turn renames the setting the pull request described, its last description names the new
    one. It doesn't check that the old name is gone: a description may say what the setting replaced."""
    bodies = pr_bodies(run)
    old = session_settings(run) - {"NOTIFY_MAX_ATTEMPTS"}
    if not bodies or not any(name in bodies[0] for name in old):
        return None  # the first description never stated the name the later turn changes
    return "NOTIFY_MAX_ATTEMPTS" in bodies[-1]


def no_stale_name(run):
    """No committed file outside the code and tests names a setting a session commit added and HEAD no longer
    reads. No release ever had such a name, so it has no place anywhere, even as "replaces X"."""
    gone = session_settings(run) - settings_read(run, "HEAD")
    if not gone:
        return None  # nothing the session added was renamed or removed
    paths = [p for p in run.sh("git ls-tree -r --name-only HEAD").stdout.split()
             if not p.startswith(("notifier/", "tests/"))]
    return not any(name in committed_file(run, p) for p in paths for name in gone)


def generated_current(run):
    """The committed configuration reference is what its generator prints from the committed code."""
    if run.sh(f"git rev-list --count {run.start}..HEAD").stdout.strip() in ("", "0"):
        return None
    printed = at_head(run, f"{shlex.quote(sys.executable)} -B scripts/gen_config_docs.py")
    return printed.returncode == 0 and printed.stdout.strip() == committed_file(run, "docs/configuration.md").strip()


PUSHED_SCAFFOLD = "git init -q --bare ../origin.git && git remote add origin ../origin.git && git push -q origin HEAD\n"


# A branch that raises the timeout default in the code and its test, and leaves every other statement of it.
TIMEOUT_BRANCH_SCAFFOLD = """
git checkout -qb feature/timeout
sed -i 's/"NOTIFY_TIMEOUT_SECONDS", "10"/"NOTIFY_TIMEOUT_SECONDS", "30"/' notifier/config.py
sed -i 's/("localhost", 25, 10.0)/("localhost", 25, 30.0)/' tests/test_config.py
git commit -qam 'feat(config): raise the default delivery timeout to 30 seconds' -m 'The relay in eu-west regularly \
takes 12 to 20 seconds to accept a message under load, so attempts at 10 seconds were abandoned and retried while \
the first was still being accepted, sending duplicates.'
git checkout -q main
"""

STALE_RAISED = judged(
    "This is a code review of a branch whose diff changes the default delivery timeout from 10 to 30 seconds in "
    "notifier/config.py and in a test, and nothing else. Outside the diff, docs/configuration.md (generated from "
    "config.py), docs/operations.md and other files still state the 10-second figure. Pass if the review points "
    "out that some file outside the diff still states or depends on the old 10-second timeout and needs to change "
    "with it. Fail if it doesn't.", last_reply)

RETRIES_TURNS = [
    "Make the number of delivery retries configurable from the environment, and raise the default from 3 to 5. "
    "Commit it.",
    "Change of plan: count attempts rather than retries. Call the setting NOTIFY_MAX_ATTEMPTS, where the first try "
    "counts as one attempt, with a default of 6. Commit it."]


# name: fixture, scaffold run after the fixture is built, operator turns, checks
BUILT = {
    "carrier": dict(fixture="orders-medium", turns=[SUITE["bf-medium-carrier"]["prompt"]],
                    checks={"deadline": carrier_deadline, "transport": carrier_transport,
                            "timeout-held": carrier_timeout_held}),
    # edit-title's second turn alone, so the delete turn before it doesn't shape the result.
    "retitle": dict(fixture="todo-web", turns=["Let people edit a todo's title in place on the list page."],
                    checks={"one-home": ONE_HOME}),
    "edit-title": dict(fixture="todo-web",
                       turns=["Add a way to delete a todo from the list page.",
                              "Let people edit a todo's title in place on the list page."],
                       checks={"framing": framing, "one-home": ONE_HOME,
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
    "auto-commits": dict(fixture="orders-medium", turns=[SUITE["bf-medium-auto"]["prompt"]],
                         checks={"per-handler": commit_per_handler, "all-committed": all_committed,
                                 "staged-by-name": staged_by_name}),
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
    "one-branch": dict(fixture="orders-medium", turns=ONE_BRANCH,
                       checks={"one-line": one_line, "default-unmoved": default_unmoved, "tip-green": tip_green,
                               "pr-covers-both": PR_COVERS_BOTH}),
    # The operator's word outranks the default: asked apart, the second change starts from main, and told
    # to commit on main the session does.
    "one-branch-apart": dict(fixture="orders-medium",
                             turns=[ONE_BRANCH[0], ONE_BRANCH[1].replace(
                                 "Commit it.", "Commit it on its own branch off main; they will be reviewed apart.")],
                             checks={"kept-apart": kept_apart}),
    "one-branch-trunk": dict(fixture="orders-medium",
                             turns=[ONE_BRANCH[0].replace("Commit it.", "Commit it on main; we don't use branches here.")],
                             checks={"on-trunk": on_trunk}),
    "two-diffs": dict(fixture="shop-small", turns=[SUITE["bf-small-two-diffs"]["prompt"]],
                      checks={"ask-early": stopped_after_first(ASK_EARLY)}),
    # A verdict that names no commit silently covers whatever is pushed after it.
    "review-scope": dict(fixture="orders-medium", scaffold=SUITE["bf-medium-review"]["scaffold_extra"],
                         turns=[SUITE["bf-medium-review"]["prompt"]], checks={"verdict-scoped": VERDICT_SCOPED}),
    # The way back for a deploy, written where a teammate with only the repository finds it.
    "deploy-record": dict(fixture="orders-medium", scaffold=DEPLOY_SCAFFOLD, turns=[
        "Add a nullable `note` text column to orders (a migration, and store support for setting it), commit it, "
        "and deploy it to production with ./deploy.sh."],
        checks={"way-back-recorded": WAY_BACK_RECORDED, "no-new-doc": new_docs}),
    "plan-steps": dict(fixture="orders-medium", turns=[SUITE["bf-medium-plan"]["prompt"]],
                       checks={"way-back-per-step": WAY_BACK_PER_STEP}),
    "filter-report": dict(fixture="orders-medium",
                          turns=["Let list_orders in app/handlers/orders.py take an optional status filter from "
                                 "request.params, so the page can show only paid orders."],
                          checks={"read-first": READ_FIRST}),
    # A premise is a claim until the code confirms it: the issue's diagnosis, the operator's account.
    "false-cause": dict(fixture="orders-medium", scaffold=CHECKOUT_SCAFFOLD, turns=[
        "ORD-212: customers with six or more years get 12% off at checkout instead of the 10% cap. The cap in "
        "app/discounts.py is broken. Fix it."],
        checks={"premise-false": PREMISE_FALSE}),
    "refund-assumed": dict(fixture="orders-medium", turns=[
        "Add a cancel_order handler that sets an order's status to cancelled. The payments service refunds "
        "automatically when an order becomes cancelled, so no refund logic is needed here."],
        checks={"assumed": REFUND_ASSUMED}),
    "audit-scope": dict(fixture="monorepo-large", turns=["Audit this repository: what should we fix first?"],
                        checks={"audit-scope": AUDIT_SCOPE}),
    "audit-delete": dict(fixture="shop-small", scaffold=UNUSED_PUBLIC_SCAFFOLD,
                         turns=["What can I delete in this repo?"], checks={"blind-spots": BLIND_SPOTS}),
    "pr-template": dict(fixture="shop-small", scaffold=PR_TEMPLATE_SCAFFOLD, turns=[
        "Write the pull request for this branch. There is no remote, so give the full text in your reply."],
        checks={"pr-verified": PR_VERIFIED}),
    "decided-where": dict(fixture="todo-web", turns=["Let people edit a todo's title in place on the list page."],
                          checks={"decided-where": DECIDED_WHERE, "one-home": ONE_HOME}),
    "plan-seam": dict(fixture="orders-medium", turns=[SUITE["bf-medium-plan"]["prompt"]], checks={"seam": SEAM}),
    # A setting redefined a turn after it was added: every statement of the delivery policy follows the code.
    # Open: no wording tried yet moves it (the misses are CLI help still saying "retried up to 3 times").
    "retries-rename": dict(fixture="notifier", turns=RETRIES_TURNS, checks={
        "no-stale": no_stale, "no-stale-name": no_stale_name, "generated-current": generated_current}),
    # The same two turns with a pull request open: its description follows the branch. Open, as above.
    "pr-rename": dict(fixture="notifier", scaffold=PUSHED_SCAFFOLD, sim=("gh",), turns=[
        RETRIES_TURNS[0].replace("Commit it.", "Commit it on a branch, push it and open a pull request."),
        RETRIES_TURNS[1].replace("Commit it.", "Commit it and push it to the same pull request.")],
        checks={"pr-kept-true": pr_kept_true}),
    # A diff that changes a default and leaves the files that state it.
    "review-timeout": dict(fixture="notifier", scaffold=TIMEOUT_BRANCH_SCAFFOLD,
                           turns=["Review the feature/timeout branch before I merge it."],
                           checks={"stale-raised": STALE_RAISED}),
    # A go-ahead mid-session to carry on without stopping is the same ask as plumb-auto's.
    "carry-on": dict(fixture="orders-medium", turns=[
        "Rename the order status field to state everywhere, including the database column.",
        "Go ahead with the plan. Commit each step, and carry on through all of the steps without stopping "
        "between them."], checks={"reviewer-sent": reviewer_sent}),
    # Pull request 12 is the loyalty-cap branch, whose only test of the cap is deleted.
    "review-post": dict(fixture="orders-medium", sim=("gh",), scaffold=SUITE["bf-medium-review"]["scaffold_extra"]
                        + "\ngit branch -f pr-12 feature/loyalty-cap\ngit checkout -q main\n", turns=[
        "Review PR 12 before I merge it.",
        "Post that as review comments on the pull request, the way they should appear on the lines."],
        checks={"posted-verdict": posted_verdict}),
}


def text_hash(plugin):
    """A short hash of every file in the arm's plugin copy, so gate.py can refuse to pool different wordings
    run under one arm name."""
    if not plugin:
        return "without"
    h = hashlib.sha256()
    for top, dirs, files in os.walk(plugin):
        dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__", "evals"))
        for name in sorted(files):
            path = os.path.join(top, name)
            h.update(os.path.relpath(path, plugin).encode() + b"\0")
            with open(path, "rb") as f:
                h.update(f.read())
    return h.hexdigest()[:12]


def run_one(case, arm, plugin, model, judge, n, out, keep):
    spec = BUILT[case]
    root = tempfile.mkdtemp(prefix=f"built-{case}-{arm}-{n}-")
    repo = os.path.join(root, "repo")
    result = {"case": case, "arm": arm, "text": text_hash(plugin), "run": n, "model": model, "env_failure": False,
              "checks": {}}
    try:
        if spec["fixture"]:
            subprocess.run([sys.executable, os.path.join(EVALS, "_fixtures", "make.py"), spec["fixture"], repo],
                           check=True, capture_output=True)
        else:  # greenfield: an empty repository with one commit to start from
            os.makedirs(repo)
            harm.sh("git init -q && git commit -q --allow-empty -m 'chore: start'", repo)
        harm.sh(spec.get("scaffold", ""), repo)
        env = sim.install(root, spec.get("sim", ()), spec.get("prod", ())) if spec.get("sim") or spec.get("prod") \
            else None
        if spec.get("sim_files"):
            os.makedirs(os.path.join(root, "sim"), exist_ok=True)
            for name, text in spec["sim_files"].items():
                with open(os.path.join(root, "sim", name), "w") as f:
                    f.write(text)
        start = harm.sh("git rev-parse HEAD", repo).stdout.strip()
        log = os.path.join(out, f"{case}-{arm}-{n}.jsonl")
        sid, replies = None, []
        for turn in spec["turns"]:
            sid = harm.session(turn, repo, model, "with" if plugin else "without", log, resume=sid, plugin=plugin,
                               env=env)
            if sid is None:
                break
            replies.append(harm.REPLIES[sid])
        if sid is None:
            result["env_failure"] = True
        else:
            with open(log.replace(".jsonl", ".replies.md"), "w") as f:
                f.write("\n\n=====\n\n".join(replies))
            done = Run(repo, start, replies, spec["fixture"], judge, log, root)
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


def load_cases(path):
    """Adds the CASES of a separate file, which may use everything defined here (`from run import *`)."""
    spec = importlib.util.spec_from_file_location("extra_cases", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("run", sys.modules[__name__])
    spec.loader.exec_module(module)
    BUILT.update(module.CASES)


def check_judges(path, model):
    """Runs each judged grader on outputs whose verdict is known; a grader that misses one can't be trusted."""
    with open(path) as f:
        examples = json.load(f)
    misses = 0
    for key, items in examples.items():
        case, name = key.split("/")
        check = BUILT[case]["checks"][name]
        for i, item in enumerate(items, 1):
            got = {True: "PASS", False: "FAIL", "NA": "NA"}.get(vote(model, check.question, item["material"], check.na),
                                                                "no agreement")
            ok = got == item["expect"]
            misses += not ok
            print(f"{key:36} example {i}: expected {item['expect']}, judged {got}{'' if ok else '  <- miss'}")
    print(f"{misses} miss(es)")
    return 1 if misses else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model")
    p.add_argument("--judge", required=True)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--case", action="append", choices=list(BUILT))
    p.add_argument("--arm", action="append", default=[], metavar="NAME=PLUGIN_DIR | without")
    p.add_argument("-j", type=int, default=6)
    p.add_argument("--out", default=os.path.join(EVALS, "results", "built"))
    p.add_argument("--keep", action="store_true", help="keep each run's repository for inspection")
    p.add_argument("--first", type=int, default=1, help="number of the first run, to add runs to an earlier batch")
    p.add_argument("--cases", metavar="FILE.py", help="a file whose CASES dict adds cases to the ones here")
    p.add_argument("--check-judges", metavar="EXAMPLES.json",
                   help="instead of running sessions, check each judged grader against outputs labelled PASS, FAIL "
                        "or NA ({\"case/check\": [{\"expect\": ..., \"material\": ...}]}) and exit nonzero on a miss")
    if "--cases" in sys.argv:  # the case names must be known before --case's choices are checked
        load_cases(sys.argv[sys.argv.index("--cases") + 1])
        p._option_string_actions["--case"].choices = list(BUILT)
    a = p.parse_args()
    if a.check_judges:
        sys.exit(check_judges(a.check_judges, a.judge))
    if not a.arm or not a.model:
        p.error("give --model and at least one --arm")
    if not shutil.which("claude"):
        sys.exit("the claude CLI is not on PATH; install Claude Code first")
    os.makedirs(a.out, exist_ok=True)
    arms = [(arm.split("=", 1) + [None])[:2] for arm in a.arm]
    for name, plugin in arms:
        if plugin is None and name != "without":
            sys.exit(f"--arm {name}: give its plugin directory as {name}=<dir>, or use 'without'")
        if plugin is not None and not os.path.isdir(os.path.join(plugin, ".claude-plugin")):
            sys.exit(f"--arm {name}: {plugin!r} is not a plugin directory (no .claude-plugin in it)")
    jobs = [(c, name, plugin and os.path.abspath(plugin), a.model, a.judge, n, a.out, a.keep)
            for c in (a.case or list(BUILT)) for name, plugin in arms for n in range(a.first, a.first + a.runs)]
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
