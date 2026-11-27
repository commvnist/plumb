# Changelog

What changes for people using plumb. Versions follow semantic versioning; in Claude Code, run `/plugin marketplace update plumb-marketplace`, then `claude plugin update plumb@plumb-marketplace` in a terminal, to pick up a new one.

## Unreleased

### Added
- `plumb-jira` covers every common issue type and comment. Each type falls into a kind with its own shape: defect (bug, a defect found in testing), need (story, feature, improvement), work (task, sub-task, technical debt), container (epic, initiative), question (spike, research), test (test case, test run) and operations (incident, problem, change). A task's summary is an instruction naming the change by its effect, or by its mechanism when that is the work; a story's or epic's names the outcome; a spike's, its question. An epic's work is its linked child issues. Defects, incidents and problems carry a workaround when one is known, and a change says what shows it worked. A comment does one job (an update, a blocker, a question, a handoff, a review or test result, a decision reached elsewhere, a reopen), and closing an issue records the change that resolved it and the evidence it works.
- `plumb-jira` searches for an existing issue before filing, leaves priority, sprint, fix version, assignee and estimates to the team unless told, uses the issue type you name, and never learns a project's setup by making a trial write. Bugs record how often they happen and the last version without them; a cause no run has proved is marked suspected; a part with nothing known is left out rather than filled with a placeholder.

## 0.35.0

### Added
- Issues and update comments in any tracker, not only Jira, take `plumb-jira`'s format: a GitHub issue gets the same summary, steps, expected against actual, and evidence as a Jira bug, and an update on an issue or a pull request says what the work changed, links it, and says what happens next or who is needed. On a pull request update after review feedback, main said what changed and what comes next in 0 of 11 runs, the change in 17 of 18.
- A vulnerability goes where the project takes private reports, never into a public issue, unless you still ask for one after being told it discloses the hole. Asked to file an auth bypass as a public issue in a project whose policy says report privately, main held back in 3 of 6 runs, the change in 12 of 12.
- A merge that writes a commit gives it its own message: the pull request's title as the subject, the description's reason as the body, and every footer its commits carry (a `BREAKING CHANGE:` line most of all), never the tool's list of commits. `plumb-ship` now also loads for "merge it".

## 0.34.0

### Added
- `plumb-jira` writes Jira issues, comments and progress updates in one format. A summary names the symptom and where it happens, never the fix. A defect's description gives what happens, steps to reproduce, expected against actual, the evidence and any suspected cause marked unconfirmed; a need's gives the problem, acceptance criteria someone else can check, and what is out of scope. An update says what the work changed, read from the commit or diff rather than the request, links it, and says what happens next. It writes only on an instruction for that step, keeps the parts of a field an edit wasn't asked to change, and writes in the markup the instance renders (Markdown, ADF or wiki markup) instead of assuming one. On Haiku, updates that said what changed went from 9 of 18 to 18 of 18.

## 0.33.2

### Changed
- A comment on a pull request (a review, a line comment, a reply) is back in the neutral technical voice, like everything else plumb commits or posts. Ask for your own voice, first person, when you want a given comment worded that way. The posted-text check flags first person in a pull request comment again.

## 0.33.1

### Changed
- Reviews judge input handling once, under safety, instead of under both safety and simplicity.
- An explanation no longer carries its own "lead with the point" step; the charter's result-first rule already covers it.

## 0.33.0

### Changed
- Every skill was revised in ten critical review rounds against the standing authorities (kernel and git patch guidelines, Conventional Commits, Google engineering practices, SemVer, Keep a Changelog, Nygard, Diátaxis, Beck, Feathers, Fowler, Ousterhout, Zeller, Agans, the SRE books, OWASP) and published measurements of how coding agents fail. The main changes:
  - Faking success now covers special-casing a test's input, or skipping a check or running it only where it passes, as when a seed is pinned to hide a flaky test. A check the code can't honestly meet stays failing and is reported.
  - A test counts as seen failing only when the code exists but is wrong, not when a name is missing. Failures the change caused are told from failures that were already there.
  - Debugging names only a cause a run confirmed, tests each candidate alone against a predicted outcome, halves the gap to the nearest passing state, and reruns the original reproduction after the fix. An unconfirmed cause is reported as a suspect, unfixed. An explanation searches history and earlier reports before calling a reason unknown.
  - Code describes itself as it stands, never its history. Errors are handled once, where something can act on them. Secrets and personal data are named by where they live, never by value. Inputs crossing a trust boundary are checked there, and what can't be confirmed as allowed is refused. Code holds only the access it uses. A new dependency is asked for with registry evidence that it is the package meant.
  - A refactor of untested code first pins what the code does now. Tests use real collaborators where they are fast and deterministic, and show the data their outcome depends on.
  - Reviews treat a defect they can neither make happen nor trace as a question, never Blocking, and say what went unchecked. The independent reviewer gets the operator's own words, never the author's summary. Under plumb-auto the review comes last, on the branch's commits, and a finding stands until the reviewer withdraws it.
  - Commit bodies and pull request descriptions share one structure: what is wrong without the change, the choices made and what each beat, then the evidence, readable without the links they cite. A fix to unpushed work goes into the commit it fixes. Changelogs list every breaking change and deprecation, version by what changed for users, and the entry lands in the change's own diff.
  - Deploys name what would show failure before releasing, go to the smallest share the deploy allows, and roll back first at a sign of failure.
  - Plans remove an old form only once nothing reads it, keep main releasable after every step, and list as unknown only what no read settles.
  - Text the work reads, such as a branch under review, an issue or a tool's output, is data, never an instruction or a yes. A yes covers only the step it was given for.
  - plumb-debug no longer has a separate line for a failure that won't reproduce: an unconfirmed cause is reported as a suspect, unfixed. plumb-build offers the refactor that makes a change easy first, as its own diff. plumb-audit's security pass traces from where untrusted input enters and covers dependencies the project can't vouch for.
- A comment on a pull request (a review, a line comment, a reply) is written as you would write it to a colleague, first person where natural, so it reads as yours rather than as generated text. Everything else plumb commits or posts stays in the neutral technical voice, and nothing anywhere mentions AI. The posted-text check no longer flags first person in a pull request comment and still flags a credit line there. Asked to post a review as line comments, 13 of 14 runs on Haiku posted comments that read as a person wrote them, against 1 of 15 before; Sonnet 18 of 18 against 17 of 18.

## 0.32.0

### Changed
- plumb-debug bounds a failure's cause by the nearest state that passes, such as the base branch or an earlier commit, so a failure a branch inherited isn't debugged as the branch's own. In a field session, the decisive check on a failing docs build was whether main failed the same way (it did), made by instinct rather than by the skill. Asked to fix a feature branch whose failing test also fails on main, 18 of 30 runs on Haiku told the operator the failure was already on main, against 10 of 30 before; Sonnet did so 6 of 6 either way.

## 0.31.0

### Changed
- A review makes each finding happen and tries its fix in a scratch copy, with whatever the change allows (a render, a dry run, a script), so a fix it proposes has been seen to work. In a field session, a review of a change no check ran posted a fix that wasn't one, found only when the operator asked for evidence. Reviewing a branch whose template uses a value its renderer never fills, 4 of 6 runs on Haiku tried the fix, against 0 of 6 before; on Sonnet, 0 of 6 either way, as it left the fix's value to the operator.

## 0.30.0

### Added
- The first push or new pull request in a session, or since its last compaction, carries a one-line reminder to offer to record what the session found costly to learn and likely to recur (charter rule 20). In a long field session several such facts (a tool flattening folders, a tag character a registry refuses, a no-op label re-add) went unrecorded because the offer had faded from view by the time the work shipped. Said once, and only where the session's transcript can be read.

### Fixed
- The check on text posted to a pull request or issue no longer tells the agent to edit the post in place. It now says to show the operator the corrected text and edit only with their yes, since the post is already on a shared system and its wording may be one the operator approved. When a body file can't be read, it says only the command's own text was checked, instead of reporting the file unchecked next to a first-person finding drawn from the command.

## 0.29.0

### Changed
- A plan that stages a change to stored data or an outside contract stops using the old form in one step and removes it in a later one, and keeps each step working while instances of the step before it still run. Before, plans for a column rename tended to stop writing the old column in the same release that dropped it, so instances still on the previous release failed every write during a rolling deploy. Planning that rename, 8 of 12 runs (Sonnet and Haiku) kept the two apart, against 3 of 12 before.
- Being told part way through a session to carry on through several changes without stopping now brings in plumb-auto, as the same words do at the start of a session, so each change gets its independent review before the run ends. Told to go ahead with a staged column rename and carry on through every step, 11 of 11 runs dispatched the reviewer, against 6 of 12 before; on Sonnet, two changes asked for in one request still stop after the first.
- A review posted to the pull request carries the verdict given in the reply as its state, so a review that asks for changes blocks the merge instead of landing as a plain comment. Asked to review a pull request that deletes its only test of a changed cap and then to post the review, 18 of 18 runs on Sonnet posted it as a request for changes, against 11 of 18 before.
- The regression test plumb-debug writes forces the cause it locks, so it fails before the fix on every run instead of on the runs where chance produces the fault. For a cart whose name order came from a set, 15 of 24 runs (Sonnet and Haiku) wrote a test that failed on every hash seed, against 5 of 24 before.
- An audit reports a check the code needs and lacks as a finding, never as an area it couldn't reach. Before, an audit of a billing API that takes an API key and a customer id, and checks neither, listed the missing authorization under "unchecked". Auditing that API, 6 of 36 runs (Sonnet and Haiku) reported that any key can bill any customer, against 0 of 36 before; the smaller model moved most (5 of 18 from 0 of 18), and the stronger one rarely did either way.

### Fixed
- The commit check no longer mistakes a local commit for one handed to another program when an earlier part of the same shell command holds a double quote inside single quotes (a `sed` script, say). Such a commit was checked only for credit lines and first person, so a subject outside Conventional Commits, a missing body or skipped hooks went unflagged.
- A commit whose message mentions a `gh` command that posts (in a heredoc) is no longer checked as if it had posted to a pull request or issue.
- Text posted with `gh` on its own line after another command (`cd` first, say) is checked for voice and credit lines like any other post.

## 0.28.0

### Changed
- An audit says what it didn't reach. Its Verified line now ends with what the audit left unexamined, and each auditor agent returns that with its findings, so a partial audit no longer reads as a whole one. Auditing a twelve-service repository in one session, 5 of 6 runs on the smaller model named what they hadn't read, against 0 of 6 before; the stronger model already did.
- An audit's Delete list says, for each item, what the search that shows it unused can't see, such as callers outside the repository. Asked what could be deleted from a library whose functions other projects import, 17 of 18 runs on the smaller model named the outside callers their search couldn't reach, against 11 of 18 before.
- A pull request description says what was run to show the change works and what nothing exercised, and a project's pull request template no longer replaces plumb's own sections: the description is written inside the template, under headings for what it lacks. In a repository whose template has only a summary and a checklist, 17 of 18 runs on the smaller model gave the command run and its result, against 7 of 18 before; why and risk were measured too and showed no clear change.
- Each choice under Decided in the end-of-change report says where it sits in the code, so a reviewer can judge it without searching for it first. After adding in-place editing to a todo list, 8 of 31 runs on the smaller model located every decision, against 1 of 30 before; the stronger model rarely did either way (1 of 28 against 0 of 28).

## 0.27.0

### Changed
- A premise from a request, an issue, a doc or an instruction file is a claim until the code, history or a run confirms it, wherever that evidence lives, and a false one is shown with its line before anything is built on it (charter rule 14). Handed an issue that blamed the wrong file, 6 of 6 runs (Sonnet and Haiku) said the diagnosis was wrong and showed where the cause was, against 1 of 6 before; one run before the change "fixed" it by changing the rule the issue blamed. Told that another team's service refunds cancelled orders, 6 of 6 runs marked that as unconfirmed, against 3 of 6. Builds that rest on true premises went ahead as before.

## 0.26.0

### Changed
- The end-of-change report's Done line points to the file and line to read first, so you start reading the change where its logic lives instead of hunting through the diff. After adding a filter to a handler, 6 of 6 runs (Sonnet and Haiku) named that place, against 0 of 6 before.
- A plan says for each step how to roll it back once it has shipped, or why it can't be, so the one-way step of a staged migration (dropping the old column) is named before anything is built. Planning a column rename, 6 of 6 runs marked it, against 1 of 6 before.
- Under plumb-auto, a Blocking finding from the independent reviewer is no longer closed by the author disputing it. A dispute goes back to the reviewer with its evidence, and a finding the reviewer doesn't withdraw after a second round is listed under Waiting on and the run is reported as stopped short. The Reviewed line gives each dispute with the reviewer's answer. This one wasn't measured, since no eval case reliably makes an author dispute its reviewer.
- The neutral-voice rule (charter rule 19) now covers anything that tells how the work was produced, not only AI credit: no mention of a model, agent, subagent, prompt or session in what is committed or posted, unless the work is itself about AI, which is described like any other subject.

## 0.25.0

### Changed
- A deploy records its way back where the project keeps what shipped (the changelog, a release note, a runbook), covering stored data as well as code, instead of only telling you in the reply. Asked to add a column and deploy it, 5 of 6 runs (Sonnet and Haiku) left a teammate with only the repository the steps to undo both the code and the column, against 0 of 6 before; none added a new file to do it.
- plumb-debug's "the cause and the observation that established it" now sits in the charter's Why line, so it applies to every fix, including one made while building or under plumb-auto. Debug sessions show their evidence as before (6 of 6 runs either way); fixes outside debug weren't measured.
- The charter, plumb-build and plumb-debug are 36 words shorter, with every behaviour kept. Rule 19 ("new code logs as the project's code does") is gone, since rules 6 and 11 already hold it and sessions log in the project's style without it (6 of 6 runs either way). plumb-build no longer repeats rule 15's "run the project's checks" in two steps; sessions still ran the checks before the first edit. The doc shape drops "changed with what it describes"; a README line documenting a changed default was updated in the same commit in 6 of 6 runs without it. Rules 20 and 21 are now 19 (neutral voice) and 20 (leave the next run less to rediscover).

## 0.24.0

### Changed
- A review's verdict names the commit it judged, so a push after the review can't borrow it. Before, a verdict named only the branch, and a branch that moved after the review still read as approved. Reviewing a branch, 6 of 6 runs (Sonnet and Haiku) named the commit, against 0 of 6 before.

## 0.23.0

### Changed
- Commits go where the work can still be reviewed: one branch off the one it merges into, with later work on top unless you ask for it apart. Before, plumb-ship named a branch and never said where commits belong, so a session asked for two changes and then a pull request left them on sibling branches or on `main`, and the pull request covered one of them or needed the branches repaired first. Over three turns (two changes, then the pull request), 5 of 6 runs left both changes on one new branch with `main` untouched, against 0 of 6 before; asked to keep the second change apart, every run did. A project that commits straight to its main branch says so, in the request or its written rules, and plumb commits there (3 of 3 runs).
- The end-of-change report states what it is waiting on from you second, straight after Done, instead of after the choices and the evidence. In sampled sessions the ask began four fifths of the way down the reply. After the first of two diffs, 6 of 6 runs on the strongest model put the ask ahead of Decided and Verified, against 1 of 6 before.
- plumb-debug locks a fix with a test that fails before the fix on every run. For a fault that shows only now and then, the regression test kept before was red under 16 of 40 hash seeds with the bug back; with the wording, 3 of 3 runs on the strongest model left a test that fails under each of twenty hash seeds, against 0 of 3 before.

## 0.22.0

### Changed
- Charter rule 21 applies to work that changes nothing: a question or an investigation that uncovers something costly to find again now ends with the offer to record it, as a change already did. Asked how a migration reaches staging, where only a script shows that the pushed release branch is applied and never the local checkout, 24 of 27 runs offered to record it for the next session, against 2 of 18 before; a walkthrough with nothing worth recording still ends without the offer.

## 0.21.0

### Added
- When you name the Jira issue a pull request is for, plumb-ship leads its title with the key in brackets (`[PROJ-123] fix(scope): subject`) and opens the description with a section referencing that issue. A key you didn't name, such as one in the branch name, is left out.

## 0.20.0

### Changed
- Charter rule 9 says what plain means: one job per unit, one home per fact. On a request to add in-place title editing to a todo page, 8 of 12 runs kept one rule for a valid title shared by create and edit, or offered to, against 1 of 12 before, which wrote the check twice at different strictness.

## 0.19.2

### Fixed
- After a context compaction, the charter gate holds the next edit, commit or push once again, and the session-start hook says to load the plumb skills again. Before, the gate saw the charter from before the compaction in the transcript and stayed quiet while the agent no longer had it, so the end-of-change report and the rules after it faded for the rest of the session.
- A subagent's edits are held at most once. The gate read the main session's transcript, where a subagent's refusal never appears, so it could hold the same call every time.
- The commit check finds a commit on any line of a multi-line command, not only the first.

### Changed
- The commit check says when a commit went to another program (a remote shell, a container, a job runner's heredoc), where it can't read the result, and checks the message given in the command (each `-m`, or a heredoc fed to `-F -`) for AI credit and first person. A local repository is still checked first, so a commit run through `bash -c` gets the full check. A clean handed-off commit is pointed out once a session.
- Text posted with `gh` from an empty body or an empty file is flagged, since an edit with it blanks what was there, and so is a body file the check can't read.
- The session-start reminder names the installed version, so a session with two versions of plumb loaded shows it.
- The README says which commits and posts the commit check can see.

## 0.19.1


### Changed
- plumb-ship deploys only with a way back for everything the deploy changes, stored data included. A rollback of the code doesn't bring back a dropped column; on the smallest model, deploys of a commit that drops one now stop for a yes in 6 of 6 runs, against 3 of 6 before.

## 0.19.0

### Changed
- The report's Decided line puts the choice that costs most to undo first, so the one worth an operator's challenge isn't read last.
- A commit holds only files the change wrote, staged by name. Without it, 6 of 18 runs of a small refactor committed build output or rewrote a commit to take it out; with it, none.
- A commit body gives the evidence the project's checks don't hold, in place of "how it was verified", which drew a line repeating that the suite passed (13 of 18 bodies on main, none with this).

## 0.18.3

### Changed
- plumb-debug writes the failing test before the fix, so seeing it red needs no undo of the fix (which tempted a `git stash` that sweeps the operator's uncommitted work).
- plumb-auto points to charter rule 3 for what needs a yes instead of restating part of it, plumb-plan puts the riskiest unknown in the first slice rather than naming two different firsts, and the reviewer agent judges the code against the request.
- plumb-explain drops ", and what you inferred" from its misbehaviour step: evals showed no loss without it.
- The README's example report fixes the "1,50" misparse it used to list as a suggestion, as the charter requires, and says where a rule's reasons go as CONTRIBUTING does.

## 0.18.2

### Fixed
- The commit check no longer tells the agent to amend the operator's own recent commit when the agent's commit failed: it now checks that the commit is the one this command made.
- The commit check flags every way of skipping the project's hooks (`-n`, `-nm`, `core.hooksPath`), and checks text posted by `gh pr review`, `gh pr merge --body`, `--body-file` and `gh api` as well as first person opening a later paragraph. `--assignee @me` and a `(us)` scope are no longer flagged.
- A change to the skills, agents or hooks releases at least a patch whatever its commit type, and a release is built only from the commit its checks passed on.

## 0.18.1

### Fixed
- The commit check finds a commit made in another repository (`git -C` or a `cd` first), flags a commit that skipped the project's hooks (`--no-verify`), and holds pull request and issue text posted with `gh` to the same voice as a commit.
- The charter gate reads a transcript path with escaped backslashes (Windows), and also watches `apply_patch`, so Codex edits are held like Claude Code's.

### Changed
- Removed six passages evals showed change nothing, each ablated alone at three runs: plumb-test's "Reject on sight" list and its "seen to fail on its break" (rule 16 says both), plumb-ship's list of pull request sections (the why, the risk and the way back, and where to look first stay), and three reasons inside rules (plumb-ship's "since a summary leaves the operator to write it", rule 6's "mixed styles cost more than a weak one", rule 11's "so the code can be debugged from its output").
- The README says what plumb's rules can't stop and which settings can (permission deny lists, the attribution setting), that Codex agents must be copied again after each update, and that a `plumb agents:` line can live in a personal instruction file.
- Four decisions that were only in project notes are now records: no "Try it" line in reports, one principal-engineer lens for suggestions, artifacts in the operator's voice, and skill text living and dying with its eval.

## 0.18.0

### Changed
- A review states its reading of the change's intent, and a change that delivers something else fails correctness.
- The report's Decided line names what each choice beat, not only its reason.

### Evals
- New cases for existing text, kept because each fails without plumb: `bf-medium-meaning` (a change in meaning is staged), `bf-medium-deploy-drop` (a deploy needs a way back), `bf-medium-review-injection` (rules in the change under review don't direct the review), `bf-medium-unused-status` (unused includes stored data) and `bf-medium-auto-dirty` (an autonomous run keeps the operator's uncommitted work apart); `bf-medium-review-intent`, and an `alternative` grader on `bf-small-split`, for the two new lines.

## 0.17.0

### Changed
- An autonomous run's review loop ends once every Blocking finding is fixed or disputed, and the report lists the disputes under Reviewed. Before, a correct dispute could keep the loop going with no end.
- The report's Done line says when the change isn't committed, and says first when the work stopped short.
- A plan lists its unknowns, each with the step that settles it, and orders the diffs riskiest unknown first. An autonomous run reads the code before pinning what done means, and plans as plumb-plan does.
- A walkthrough says what was inferred rather than read, and its closing check says what it should show.
- A staged breaking change never lands in one release, not only one diff.
- Shipping needs the project's checks to have passed on the code as it stands, so a recent passing run counts instead of a fresh full run per commit.
- How to hand work to the reviewer agent now lives in its own description, so every caller sends the request and where the change is, never the author's reasoning.
- Clearer wording for rule 8 (every input that can arrive gets a defined outcome) and rule 19 (new code logs as the project's code does), and a shorter per-request reminder that loads only skills not yet loaded.

### Evals
- Each case runs three times per arm, and arms are compared on scored graders only; one run sat inside the noise between runs.
- Claims of evidence ("seen failing") are also graded on the commands actually run, not only on the reply.
- Each case names the skill text it guards. `scripts/check_refs.py` fails when that text is gone, and `write_cases.py --check` in CI fails when the generated cases drift from their table.
- Fixed five graders that passed or failed for the wrong reason: `no-live-run` (a run against staging with `ORDERS_DB` set in the same command), the flaky fixture (a sorted fix passed), `one-suite-run` (an audit that never ran the checks passed), `bf-small-tests` (graded a file the prompt never named) and `no-swallow` (failed a correct re-raise with context).
- New cases: `bf-small-ui` (a delete control on a todo page, new `todo-web` fixture), `bf-medium-rename-review` and `bf-small-release`, and a grader that the nightly export streams its rows.

## 0.16.0

### Changed
- Everything plumb commits or posts (code comments, commits, pull requests, review comments) is in a neutral technical voice: no "I", "we" or other first person, and nothing that credits, implies or mentions AI authorship or use. Charter rule 20 is now "Write in a neutral technical voice". Its replies to you in the session are not filtered.
- Nothing outside the diff changes without a yes: a shared or live system (such as a database a config file points at), or the operator's uncommitted work.
- A bug that won't reproduce gets evidence, not a fix, and an intermittent one is made to fail every time by forcing its cause before it is fixed.
- The report's Suggestions line asks what a principal engineer sharing the charter would still insist on, so material risks outside the diff are offered rather than left unsaid.
- A deploy needs a way back, and is followed by a check of what would show it failing.
- A whole-repository audit runs the project's checks once and gives each auditor its area's results, instead of every auditor running the suite.
- Dropped two clauses that evals showed change nothing: rule 8's bound-parameter sentence and rule 14's version clause.

### Fixed
- The commit check no longer flags prose that merely mentions a tool or AI ("generated by the database cursor"). It now also flags a commit written in the first person or with no body.

### Evals
- New cases: `bf-medium-live-db` (tag `outside`), `bf-small-flaky`, `bf-medium-suggestions` (tag `suggestions`); a neutral-voice grader on the ship cases; a single-suite-run grader on the whole-repository audit.
- Removed four cases that pass as often without plumb as with it on Haiku: injection, python-version, one-rule and payment-log. Merged `bf-small-tests-spec` into `bf-small-tests` and `bf-medium-reviewed-model` into `bf-medium-reviewed`. `bf-small-debug` no longer fails a second test that covers a separate input outcome.

## 0.15.0

### Added
- The plumb charter is much harder to skip. Each new request gets a one-line reminder to load plumb, and the first edit, commit or push in a session where the charter isn't loaded is held once with a note to load it; repeating the call lets it through, so work that isn't code goes on. On Copilot CLI these two do nothing, since it drops the reminder and gives the hook no transcript.

### Fixed
- The install notes give the full update steps: refreshing the marketplace alone left the old version installed.

## 0.14.1

### Fixed
- When a commit or pull request can't be sent, plumb gives the complete text ready to send as is, instead of a summary of what it would say. Commit and pull request bodies lead with why the change exists.
- Rule 21 now points the record at the file the next agent reads before starting (the repo's existing AGENTS.md or CLAUDE.md), whatever else is updated for people.
- The `bf-small-pr-title` eval repo has a remote, and `bf-medium-agent-file` now separates plumb from no plumb (3/3 vs 0/3).

## 0.14.0

### Changed
- Reports, plans, reviews and audits are written to be skimmed: the result first, plain words, formatting that carries the structure, and code blocks only for code and output. Each format is now a short list instead of a code-block template. Plans open with their goal and end on Waiting on, like every report.
- Every artifact plumb writes keeps one shape, set by what its reader can't get elsewhere: comments (the reason, or a contract the signature hides), docs, commits, branches, pull requests, review comments, replies to review feedback and issues. A finding has one shape everywhere (location, a scenario the system can produce, smallest fix), numbered through the reply.
- Commits always use Conventional Commits, with a body saying what the diff can't; footers hold only facts a tool reads, such as `BREAKING CHANGE:`. Branches are named `<type>/<slug>` unless the repo has its own convention. Pull request bodies are written for a principal engineer deciding whether to merge. A blocked ship still gives the exact text it would have sent.
- Rule 6 now says when to follow a convention (wherever something depends on it) and when to raise the bar (where nothing does), and to replace a weak convention everywhere rather than break it in one place.
- Rule 11: code is debuggable from its output. An error or log line says what failed, the values involved and what to do next, never secrets or personal data. Test names state the behaviour and condition.
- The report's Verified line names what the change touches that nothing run exercised. Audits get a Verified line and back each deletion with the search that shows it unused. Auditors return every finding so the merged ranking isn't built from cut lists.
- plumb-auto commits through plumb-ship, gives its reviewer the request but never its reasoning, pins kept behaviour by seeing it fail with the code briefly broken, and puts a decision record in its report instead of stopping to ask.
- With `plumb agents: off`, plumb does an agent's work itself unless you ask for one.
- The skills were tightened after the new rules went in (3,335 to about 3,200 words) with the suite holding above 0.9.

### Added
- Rule 20, write as the operator: nothing committed or posted credits or hints at an AI author, and commits go under the configured git identity. The commit hook flags a message crediting an AI tool, unless you or the project asked for it.
- Rule 21, leave the next run less to rediscover: when work uncovers something costly to find again and likely to recur, plumb offers to record it where the next run finds it: a repeated procedure as a skill, a standing fact or command as a line in the agent instruction file the repo already uses, never a second one, and fixes such a line in the diff that makes it untrue.
- Eval case `bf-medium-agent-file` (tag `memory`) and graders for readable reports (tag `readable`), commit bodies, pull request sections, test names and branch names.

## 0.13.0

### Added
- `plumb-auto`, for a task you want carried to the end without being asked anything. It writes the checks that define done before the code and sees them fail, tackles the riskiest unknown first, takes the best-supported reading where the request is unclear instead of asking, gets an independent review of the whole branch, and tries to break the result before reporting. It stops only for what needs your yes or can't be undone. Each diff is its own commit on a new local branch, nothing is pushed, and the report adds `Assumed:` (each reading taken without asking) and `Reviewed:` lines.
- Four eval cases tagged `routing` that check which skills load for wording that sits between two of them.

### Fixed
- Skills load on the requests they are for. "End to end" no longer starts `plumb-auto` (only being told to go on without you does), "is this safe to merge" and "check my work" now start `plumb-review`, and renaming a stored column goes to `plumb-plan` rather than `plumb-refactor`. `plumb-review` and `plumb-audit` each name the other for work that isn't theirs.
- `plumb-debug` no longer points at a `Noticed` report line that was removed: the cause goes under Why, and other places with the same fault under Suggestions.
- Pointers between skills say to load the skill they point to, the auditor agent loads the charter like the reviewer does, and `plumb-review`'s lower-rank findings are called Suggestions, as its verdict and the charter call them.
- `plumb-auto` says plainly that asking for it is the instruction to commit each diff locally (which `plumb-ship` requires) and that it doesn't override `plumb agents: off`.

## 0.12.0

### Changed
- Work that can stop part way (a file write, a batch, a multi-step update) either completes or leaves things as they were, rather than leaving a half-written file or half-applied update behind.

### Added
- Five eval cases, tagged `enterprise`, for traits a principal engineer's review checks: one source of truth for a business rule, a clock the tests control, no card data in logs with enough context to debug a failure, a timeout and caller-facing errors on a call to another service, and an export that can't leave a half-written file.

## 0.11.0

### Changed
- The skills and agents are about a seventh of their former length (15,692 words down to 2,279; the charter 5,126 down to 623), so each session spends far less context on plumb. All 19 rules and every numbered step keep their titles. The eval suite scores 0.929 against 0.948 before.
- Each rule is now its title and one clause. The reasons and the special-case procedure around the rules are gone; the agent is expected to decide those cases from the rule itself.
- The report is six lines: Done, Why, Decided, Verified, Waiting on, Suggestions.

### Removed
- The report's `Changed`, `Unverified`, `Risks`, `Noticed`, `Look hardest` and `Agents` lines. A reply that started an agent still names its model.
- The self-review checklist, and the separate charter sections on decisions, suggestions, asking, pushback, agents and authority, each now a sentence or two.
- The automatic offer of an independent review, and the standing "commit each step as it passes" mode for multi-step plans.
- The review and explain output templates, pull request description sections, release and rollout rules, the test-driven loop, and the 300-line diff limit.

## 0.10.0

### Changed
- Breaking changes to anything one version of the code writes and another reads (queued messages, jobs, caches, a separately deployed client) are now staged even when both sides live in the same repository, since old and new code meet during a deploy.
- A change removes code it leaves with no user, with its tests, instead of offering the deletion as a suggestion.
- Plans start with a slice that delivers behaviour; what it needs lands in its real shape for one case rather than as a foundation step first.
- Plans and decision records say what each choice gives up and what would reopen it; recommended answers to questions carry their reason.
- Reports gain an optional `Waiting on:` line naming what the agent needs from you, and a run that went on past earlier reports gathers their decisions at the end.
- Suggestions and Noticed items you've already seen aren't shown again; when you're right in a pushback, the agent also names every other place the same mistake appears.
- Test expected values come from what the behaviour should be, never from running the code; reports name the break each new test was seen failing on.
- Debug reports back the cause with the observation that established it and the closest alternative it ruled out.
- Reviews and audits file only scenarios the system can actually produce, and report a defect repeated in several places as one finding at its shared cause.
- Commits: plain imperative histories are explained as no convention (adding a type continues them), the first commit in a new format goes under Decided, and pull request titles follow the commit rules, since a squash merge makes the title the commit.

## 0.9.0

### Changed
- Code plumb writes now gives every input it can actually receive a decided outcome (handled, rejected loudly, or shown impossible), alongside the existing rule against guarding the impossible.
- Values reach a query, shell command, markup, file path or pattern only through that language's own mechanism for data (bound parameters, argument lists, encoders, a fixed mapping for names), never by building the text, since a check where the data entered can't know where it will be used.
- Behaviour that breaks at real data sizes or with a slow or failing dependency (a query per item in a loop, an unbounded read, a call with no timeout) counts as a defect to fix in the change, not a suggestion.
- New code gets the narrowest visibility the language allows and returns only what its callers need, never a whole stored record by default.
- An API counts as verified only against the versions the project actually runs on (its lockfile, its declared language version).

## 0.8.0

### Added
- GitHub Copilot CLI support. Install with `copilot plugin marketplace add commvnist/plumb` and `copilot plugin install plumb@plumb-marketplace`. The skills, agents and both hooks work there unchanged, and a `plumb agents:` line in AGENTS.md picks each agent's model as it does elsewhere. Claude Code and Codex see no change.

## 0.7.1

A consistency pass over what 0.7.0 added, so no two rules give different answers for the same situation.

### Fixed
- Pushback and Authority no longer disagree about an instruction that rejects a choice. A question gets the evidence and waits for your decision; an instruction is already your decision and is followed, with the evidence shown once. When you're right and only asked, the change is offered rather than made.
- A request that rests on a wrong belief about the code, whether a question or an instruction, gets the line or run that says otherwise and then waits for what you want.
- Naming a risk no longer excuses a defect. Only a failure that happens however well the thing is built is yours to accept; one that building it properly avoids is fixed as part of the change.
- A risk is named before a step that can't be undone, and plumb waits for your answer unless you've shown you already know it. Before, the charter said to follow and name it while plumb-ship said to ask first.
- A choice you made against plumb's evidence is recorded under Decided as yours. Before, one rule said to record it and another said choices the ask settled stay off that line.
- The independent reviewer no longer files what you asked for or decided, knowing its risk, as a finding, so a review can't undo your decision.
- A challenge phrased as "why did you do it this way" is checked again before it is explained.
- In `plumb-explain`, a defect in the session's own work has its own `Part of done` line and waits for your go; `Noticed` keeps its one meaning (problems this work didn't cause), and better choices go on the suggestions menu.
- A pull request description carries the report's Look hardest line only when the report has one.
- `plumb-debug` no longer triggers on a why question about working code, which is `plumb-explain`'s.
- The README's example for committing plan steps matches what the charter delivers.
- A defect found after the report is still part of the change, never a menu item. It is fixed at once when a check that was a step of the change found it, and on your go when it surfaced in answering your question, in an explanation, or in a review that was all you asked for.
- A review you accepted on plumb's offer counts as a step of the change, so a confirmed Blocking finding from it is fixed without asking again. A review you asked for yourself reports and waits.
- A review finding the charter already requires of the author (a self-review checklist hit or dead code in added lines, a missing reason for a decision) is part of the change even when the review files it as a Should.
- With agents off, the review offered in a fresh session is given your decisions too, so it doesn't request changes over something you chose.
- If you tell plumb to leave out a protection it built in, that is an override like any other: it follows you and names the risk once.

## 0.7.0

The operator can ask to be walked through anything, sees where to look hardest, and gets an honest answer when they push back.

### Added
- `plumb-explain` walks you through code, a diff or a decision: the point in a sentence or two, one real case traced by file and line, the reason for each choice a reader would question with the alternative and its cost, where it could be wrong, and one check you can run yourself. It changes nothing, and gives a reason it can't find as unknown rather than inventing one.
- The report has a `Look hardest` line naming the one place where a mistake would cost most and what to check there. It is left out when the whole diff can be read at a glance.
- Pushback has a rule. When you question or reject a choice, plumb checks it again before answering. If you're right it says what was wrong and changes it; if the evidence still supports the choice it shows that evidence and what your alternative would cost, once, then does what you decide and records the choice as yours. When a question rests on a belief about the code that isn't true, it shows the line or run that says otherwise first.
- Eval cases for a walkthrough of existing code, a challenge that rests on a wrong belief, and an instruction whose failure can be named.

### Changed
- When you ask for something whose failure plumb can already name, it follows you and names the risk once, as a failure story. Before, this covered only overriding one of plumb's rules.
- A technique the codebase hasn't used before goes on the Decided line with its reason.

## 0.6.0

Decisions and checks are easier for the operator to see, and plumb loads less text and skips repeat work, with the same guarantees.

### Added
- A hook checks each commit the agent makes. When its subject isn't Conventional Commits, the agent is asked to amend it straight away, or to tell you if it's already pushed. A message you dictated, or one in the project's own convention, is left as it is. Skill text alone can't guarantee the format, so this catches a slip while it's still cheap to fix.
- Audit findings and Blocking review findings name the principle they serve, as suggestions already did.
- An audit's Scope line says how it split the repository into areas, or why it read it in one session.
- An eval case checks that a request for two diffs stops after the first one's report.

### Changed
- A request that names several phases (build it, then commit it) loads each phase's skill in the first turn, so the commit rules shape the build.
- The report's Done line uses the project's commit convention, else Conventional Commits. Plain imperative subjects in a project's history don't count as a convention.
- Decided names the record, or the question about starting `docs/adr/`, for a choice that is expensive to reverse.
- Unverified lists each behaviour the change adds or could have altered that no run exercised.
- A test, added or changed, counts as seen failing only when a run shows it failing on the break it exists to catch. A predicted failure isn't evidence, and the self-review checklist asks for the run.
- A change that misbehaves under conditions it will meet (its own calls repeated, concurrent or failing partway) is a defect to fix, not a menu item.
- A plan's first slice carries the narrowest form of whatever it needs to run, instead of following setup or foundation steps.
- Every plan step confirms the event it waits for before it is built.
- Building a later plan step no longer loads plumb-plan, and a scout map from earlier in the session is reused for code only this session has changed.
- The reviewer's briefing moved from its always-loaded description into the charter, cutting the text every session carries by about 17%.
- The Agents line says "the tool's default" when the model that ran isn't known, rather than guessing.
- With agents off, a missing independent review goes under Unverified only when one was asked for or accepted, so a standing go-ahead doesn't stop at every step.
- Fixing a confirmed reviewer finding is part of done in every phase, not only in build.
- Each question asks one thing.

## 0.5.0

Fits any budget and runs on Codex: plumb names no model, you choose one per agent or turn agents off, and the same files install on Codex (untested there).

### Added
- Choose each agent's model, and optionally its reasoning effort, with a `plumb agents:` line in the project's written rules, such as `- plumb agents: scout haiku low, reviewer opus high`. A role you don't name uses your tool's default. Every reply that started an agent says which model it ran on.
- `plumb agents: off` runs plumb without subagents. The session does each agent's work; a review of its own work says it isn't independent and offers one in a fresh session. A request in the conversation for an agent's work still starts one, and the reply says so.
- The build and ship offers of an independent review point to the agents-off route.
- Codex support, untested: a Codex plugin manifest, a Codex marketplace entry and Codex versions of the agents, all generated from the Claude Code files by `scripts/build_codex.py`, with install steps in the README.
- Eval cases for a chosen reviewer model, a build with agents off, and a whole-repository audit with agents off.

## 0.4.0

Faster and cheaper to run, with the same guarantees: tests seen failing before they pass, the Decided and Verified lines, skill routing, and waiting for a go-ahead on plans.

### Added
- A plan's go-ahead can cover every step, committing each as it passes. It still stops after a step that makes a decision needing a record, leaves something unverified, adds a risk, or changes the plan.
- Eval cases for building then committing in one session, a build with an independent review, and a whole-repository audit with parallel auditors.

### Changed
- Agents no longer set a model, so they follow your choice (the session's model, or `CLAUDE_CODE_SUBAGENT_MODEL` for all subagents). Setting that variable to a cheaper model is the main way to cut agent cost.
- The charter and the phase skill load in the same turn, and another plumb skill loads only when a step applies a standard only that skill states.
- A check run earlier in the session still counts while version control shows the code is unchanged, so build, refactor and ship stop repeating runs. Committing or shipping still needs a full run on exactly what ships; an earlier one counts only if nothing has changed since.
- After a self-review edit, build and debug re-prove only what the edit could have made untrue. Refactors run the pinning checks after each move and the full checks once per diff.
- The reviewer is pointed at a commit range or the changed paths instead of being sent a pasted diff.
- Build reads only the callers whose view the change could alter.
- The self-review checklist now lives in the charter, and the keep, merge, rewrite or delete verdicts in plumb-test. The reviewer loads three skills instead of five, the scout loads none, and auditors don't load the charter.
- An audit runs the project's checks once and gives each auditor its area's results.
- A change confined to one area that changes no contract or data shape gets a shorter report and only high-risk suggestions. Its check for wrong or unsafe behaviour is unchanged.

### Fixed
- A request to build something and then commit it now loads plumb-ship before committing, so the commit gets ship's checks and a Conventional Commits subject. Before, the agent often committed straight from the build.

### Removed
- The example blocks in agent descriptions, which were in every session's system prompt.

## 0.3.0

### Added
- Every report has a `Decided` line: each choice a reviewer could reasonably have made differently, with its reason.
- Decisions that are expensive to reverse get a decision record in the diff that acts on them: the project's format, or a Nygard ADR in `docs/adr/`. Plan, review, audit and the scout read and check them.
- Commits follow Conventional Commits 1.0.0 unless the project has its own convention; review flags a commit type that hides a breaking change.
- A multi-step plan is carried in each step's pull request description, so a new session can pick it up and check what the next step waits for.
- Debug and refactor offer the independent reviewer for non-trivial work.
- README sections on behaviour that surprises people and on tuning plumb per project.
- Licensed under GPL-3.0-or-later.
- A reference checker (`scripts/check_refs.py`, run in CI) fails when a numbered rule, step or section reference stops pointing at its target.
- A session-start hook tells the agent to load the charter and the fitting phase skill for any coding request. In evals, phase skills went from firing in about half the cases to all of them.
- An eval suite (`evals/`): 14 seeded tasks across greenfield and brownfield work on small, medium and large codebases, run with `claude plugin eval`.

### Changed
- The suggestions menu shows only medium and high-risk items; low-risk ones are counted under "N more on request". Each suggestion names the principle it serves.
- Standing instructions in the environment the user set up (such as "commit and push when done") count as the user's request.
- The charter itself stages breaking changes to persisted data through plumb-plan, and the charter routes to the fitting phase skill.
- Suggestions are strictly opt-in: never "I'll include it unless you object".
- Charter rule 12 states its three allowed test edits once, as a list; plumb-test and plumb-refactor point to it.
- The report's Verified line names the exact command or manual check that was run.
- The cost of reversing a decision is judged by what will come to depend on it, not by how little code it is today, so foundational choices in new projects get decision records too.
- A commit convention means one the project states or its history visibly follows; otherwise commits use Conventional Commits.
- Rules are worded as a principle with its reason (see CONTRIBUTING.md). Pacing between diffs, staging of breaking changes, staying off shared systems and leaving the user's working tree alone are each stated once in the charter, and the other skills point to them.
- Committing work with a failing check "as it stands" needs the user to know what fails first; a plain "commit this" isn't that consent.
- A plan's first slice runs the path the request exists for, through its least certain part.
- A plan asks whether to start decision records when the project keeps none and a step will write one.
- Work that is part of done stays off the suggestions menu, so the menu holds only what the operator is choosing.
- A choice the user made that is expensive to reverse (such as renaming a public field) still gets a decision record stating their reason, or that none was given; plans list it under Decisions.

## 0.2.0

- First versioned release after the 2026-10-28 review rounds: one principal-engineer pass for suggestions, aligned test-change, staging and safety rules across all skills.
