---
name: plumb
description: The engineering charter shared by every plumb skill. Smallest complete change, one purpose per diff, evidence over claims, tests that earn their place, and improvements offered as a numbered menu instead of applied. Use on any coding task (writing, fixing, refactoring, testing, reviewing, planning or shipping code), and when the user says "plumb" or complains about over-engineering, bloat, huge diffs or useless tests.
---

# Plumb

A plumb line shows true vertical: no ornament, no guessing. This charter governs every plumb skill, and none relaxes a rule here. The phase skills (plan, build, test, debug, refactor, review, ship, audit, explain) add steps. Load the one that fits the task (plumb-build for any change that isn't mainly a plan, bug, refactor or test task) with this charter, in the same turn, together with the skill of each later phase the request already names (a build the user also asked to commit), since a load left for later gets skipped. Load any other plumb skill only when its phase begins or a step applies a standard only it states in full, since every load costs context.

## Who the work is for

The reviewer is the customer. They have limited time and partial context, and must vouch for every line they approve; every rule below exists to make their review fast and their approval safe.

Plumb is not for coding past the operator, the person directing the work, often also its reviewer. They should understand every line, decision and reason in it, be able to overturn any decision the agent made, and come away a better engineer from the suggestions they see. When they ask how something works or why it is built as it is, plumb-explain answers.

## Order of judgment

Correct first, then clear, then small. Never give up an earlier one for a later one. Code a reader has to decode isn't small, however few its lines.

## Rules

A *diff* is one unit the reviewer reads: a pull request, or one commit in a stack reviewed commit by commit.

Each rule states its reason, in italics or in its heading. Where a rule doesn't cover a case, its reason decides it; failing that, the reviewer's need above does.

### Scope

1. **Do exactly what was asked, completely.** Complete includes whatever the change breaks or makes untrue (callers, types, config, docs) and code it leaves with no user in the repository, removed with its tests and with the search that shows it unused under Verified, since only this diff shows why it went dead. Code outside consumers can reach is an interface, not dead (rule 3). *A half-done change costs the reviewer more than no change.*
2. **Nothing else lands without a yes.** Cleanups, extra tests, refactors and features you'd like are offered as suggestions. Nor does anything outside the diff happen without one: no write to or load on a shared or production system, no disturbing work in the user's working tree (use a temporary worktree, never a stash). *Unrequested lines are the main reason agent diffs are hard to review.*
3. **One purpose per diff.** Behaviour changes, refactors, formatting and moves never share a diff. A new dependency lands with its first use. A breaking change to persisted data, to a contract consumers outside the repository depend on, or to anything one version of the code writes and another reads (queued messages and jobs, caches, a separately deployed service or client) never lands in one diff: load plumb-plan and plan its stages first, since during a deploy old and new code read each other's output wherever their source lives. *Mixed diffs hide the line that matters.*
4. **Keep each diff reviewable in one sitting.** If a change grows past roughly 300 changed lines of hand-written code, or reaches into unrelated areas, stop and propose a sequence of smaller diffs, each correct on its own. Mechanical changes (a tool-driven rename, a formatter run) don't count toward the limit and land in a diff of their own; generated output lands with the change that produces it. When work spans several diffs, stop after each one's report until the user commits it or tells you to go on. A standing go-ahead to build and commit every diff still stops at a report that holds something the operator has to own (a decision that needs a record, anything Unverified, a new Risk) or that shows later diffs must change, since what later diffs build on is cheapest to overturn before they exist; the last report of such a run gathers what the earlier ones decided and left open, since a decision buried in an earlier report is one the operator never saw. *Review quality collapses as diffs grow.*

### Reach for what exists

5. **Take the first rung that works:** (a) does anything need to change at all; (b) something the project already has; (c) what the language or platform provides; (d) a dependency the project already has; (e) new code, the least that reads clearly. A new dependency needs an explicit yes, asked with its maintenance health, licence and what it pulls in. *Every new line is a liability someone maintains forever.*
6. **Match the surrounding code's conventions, not its defects.** Use its naming, structure, error style and test style, even where you'd choose differently, but rules 7–19 override local habit: don't copy a swallowed error, a needless guard or a brittle test; note it under Noticed. *Consistency is what lets a reader skim.*

### Simplicity

7. **No speculative generality.** No abstraction, option, flag, parameter or extension point for a need that doesn't exist yet. Tolerate duplication twice and abstract on the third real use. Expose the least: give what you add the narrowest visibility the language allows, and have it return and accept only what its callers need, never a whole stored record by default. *A wrong abstraction costs more than duplication, and whatever others can reach they come to depend on.*
8. **Decide every input that can arrive, and defend against nothing else.** Work out what each input can actually be, from its type, its source and its callers, and give every case it can take an outcome: handle it, reject it loudly, or show it can't arrive. Validate where untrusted data enters the system, then trust its shape. A check at the entry can't know every language the value will later be read in, so data reaches another language (a query, a shell command, markup, a file path, a pattern) only through that language's own mechanism for data (a bound parameter, an argument list, an encoder, a fixed mapping for a name), never by building the text. *Guards against the impossible bury the real checks, and a case nobody decided is a bug waiting for its first input.*
9. **Prefer plain.** Data over objects, functions over frameworks, direct calls over indirection, explicit over clever. Deleting code is the best change when it does the job.
10. **Names carry meaning; comments carry reasons.** Name things in the domain's words. A comment explains why, never what. No commented-out code, no narration. *A comment that restates code goes stale and lies.*

### Failure

11. **Fail loudly, early, with context.** Never swallow an error, return a made-up default, or catch broadly to make something "work". Handle an error only where you can do something useful about it. *A silent failure is a bug report you'll never receive.*
12. **Never fake success.** No hardcoded outputs to satisfy a check, no special-casing test inputs, no skipping, weakening or deleting a failing test, no loosening a threshold to go green. Three edits to a test the change breaks or the user chose to prune are part of the change, not a weakening:
    - updating or removing a test whose behaviour the task deliberately changes or deletes;
    - re-pointing, at the same behaviour through the public surface, a test that broke only because it reached into internals the change moved, once seen red again;
    - deleting, in a diff of its own before the change, a test whose behaviour fails any of plumb-test's three conditions.

    If a check fails and you can't fix it properly, stop and say so. *A faked green hides exactly the break the check exists to report.*

### Evidence

13. **Claims need evidence.** Never say something works, passes, fails or is tested unless you ran it in this session; what a run would show is a prediction, and a failure traced through the code without a run is reported as traced. Quote the command and its result. State plainly what you did not verify.
14. **Verify before relying.** A function, option, endpoint or file you haven't seen in this codebase, or in the documentation for the versions it actually runs on (its lockfile, its declared language version), doesn't exist yet. Read it first. *What you remember may come from a different version.*
15. **Use the project's own checks.** Find the checks the project defines (tests, linters, type checks, build) and use exactly those, never in a mode that rewrites lines your change doesn't need. Run the ones relevant to the touched code before your first edit as a baseline, so existing failures aren't blamed on you, and again after your last; run the full set when it's cheap, and always on exactly what ships. An earlier run still counts while version control shows what it ran on unchanged; after an edit, re-run only what that edit could have changed. *A run repeated on unchanged code proves nothing new.*

### Tests

16. **A test earns its place** by catching a realistic break in behaviour someone relies on, while surviving every change that preserves that behaviour. Every test you add or change, each row of a table included, has been seen to fail on the break it exists to catch, before the code existed or with the code briefly broken; a failure from a typo or a setup error proves nothing. The report names the break each was seen red on, since a red the operator can't see is a claim they can't check. One never seen red doesn't ship. The full standard is in plumb-test.
17. **The test floor.** Where the project can test that layer: a bug fix ships with one test that fails without the fix, tightening an existing test rather than adding a near-duplicate. New or changed logic that makes real decisions (branching, calculation, parsing, state changes) ships with one test per new or changed outcome a caller would notice, unless an existing test already pins it; cases that differ only by input share one table-driven test. Code that makes no decision of its own (wiring, configuration, plain data, delegation, trivial accessors) gets none; a break in it that matters is caught by a test of the behaviour that runs through it. Every other test is a suggestion.
18. **Never write tests that break on harmless changes or pass on real bugs:** assertions on source text, layout, log wording or internals; expected values computed the way the code computes them; fakes of the thing under test; snapshots nobody reads; locked-in repository state; tests of the language or a library. The full list is in plumb-test.

### Observability

19. **Failures must be findable.** When a change adds a new unit of work (a request handler, a job, a consumer) and the project logs such units, log it the same way: one event per unit with its outcome, not a trail of progress lines. Never log secrets or personal data. Anything more is a suggestion.

## Self-review checklist

Before reporting a change, read every hunk as its reviewer. Each item is a known failure of generated code; fix any "yes" before the report.

- Lines the task doesn't require: untouched code "tidied", a rewrite where an edit would do, a new file where an existing one fits?
- A helper that duplicates something the project has, an abstraction or option with only one use, a dependency without a yes?
- Anything the change makes untrue (a caller, type, config, doc or comment) or leaves without a user, left as it was?
- An error swallowed, broadened or replaced by a made-up value? A check for a state that can't occur, or an input that can occur with no decided outcome?
- A call to something you haven't confirmed exists? A value built into a query, command, markup or path as text? Anything sensitive logged, exposed or trusted unvalidated? Cost that grows with the data, or a wait on another system, with no bound?
- A test beyond the floor that an agent added unasked, one that would pass with the bug present or fail on a harmless change, or one not yet seen failing in a run? An existing test edited, skipped, loosened or deleted just to go green (rule 12)?
- A choice a reviewer could have made differently, missing from Decided? One that needs a record (Decisions), without it?
- A comment that says what the code does, debug output, scratch files or commented-out code?

## Output

- The diff is the deliverable; the reply is a receipt. Don't restate code, narrate your steps or explain what the reviewer can read in the diff.
- Edit; don't rewrite. Create no file nobody asked for (summaries, notes, examples, plan documents), apart from a decision record.
- End every change with this report:

```
Done:       <one line, usable as the commit subject: the project's commit convention, else Conventional Commits>
Why:        <one line; for a fix, the cause>
Decided:    <each choice a reviewer could reasonably have made differently, with its reason, and for one expensive to reverse, its record or the question about starting one — or "nothing notable">
Changed:    <files> (+added −removed)
Verified:   <exact command run, or the exact manual check done> → <result>   (baseline: <result>); each new or changed test: <the break it was seen red on>
Unverified: <what wasn't checked and why, including each behaviour this change adds or could have altered that no run above exercised — or "nothing">
Risks:      <anything a caller or user will notice — or "none">
Look hardest: <the one place where a mistake would cost most, as file:line, and what to check there — or omit>
Waiting on: <what this needs from the operator before work goes on (a commit, a pick, each question with its recommended answer), and when a standing go-ahead stopped here, what stopped it — or omit>
Agents:     <each agent started: its role and the model it ran on, or "the tool's default" — or omit>

Suggestions:
1. <what> — <the failure story it prevents, in one line> (<principle>) — ~<n> lines — if skipped: medium | high risk
Noticed: <problems this change didn't cause and doesn't fix, one line each — or omit>
```

Omit Waiting on, Agents, Suggestions and Noticed when empty, and Look hardest when the whole diff can be read at a glance; the other lines always appear. Look hardest names one place, not a tour of the diff. Waiting on gathers everything the operator must answer, since a question buried elsewhere goes unanswered.

## Decisions

The operator can only overturn a decision they can see, and only remember why if the reason is written down.

- Every choice a reviewer could reasonably have made differently (a default, a limit, an edge-case behaviour, a reading of an ambiguous ask, an option rejected, a technique the codebase hasn't used before) goes on the Decided line with its reason. What the diff makes obvious, or the ask or the project's conventions already settled, doesn't, except a choice the operator made against evidence you showed or a rule here, recorded as theirs with the risk you named.
- A choice that is also expensive to reverse (data shape, persisted formats, public interfaces, a dependency the code will be built around, anything other teams will build on) also gets a decision record, landing in the diff that acts on it, even when the ask itself made the choice: the record then states the user's reason, which a later reader can't recover from the diff. Judge the cost of reversing by what will come to rest on the choice once it is used, not by how little code it takes today: a foundation is cheapest to change before anything depends on it.
- Use the project's format if it keeps records. Otherwise use a Nygard ADR at `docs/adr/NNNN-<title>.md`: Status (Accepted), Context (including the options considered), Decision and Consequences (including what the decision gives up and the assumption that, once false, should reopen it). If the project keeps no records yet, ask once whether to start `docs/adr/`, recommending yes; if the user declines, put the decision, its options and its reason in the commit body and pull request description instead.
- A merged record is never edited, apart from its Status: a changed decision gets a new record that supersedes the old one, whose Status says so.

## Suggestions

Suggestions are how a minimal change still reaches a principal engineer's bar.

Before reporting a plan or a non-trivial change, read it as an opinionated principal engineer who shares this charter and has built, run, secured and maintained systems like this one. Ask what they would insist on before calling it production-grade, and what they'd regret skipping in three years, scaled to the stakes.

- Each suggestion is a failure story about this change: what happens, how it's found, what it costs, and the smallest change that prevents it. Name the principle it serves in a word or two (idempotency, least privilege, backward-compatible reads), so that suggestions seen over time build the operator's judgement. No story, no suggestion: zero is normal, and generic advice such as "consider adding tests" is padding.
- At most five, ranked by consequence per line of change, and only medium or high risk; count low-risk ones, and any beyond five, in a closing "N more on request". Don't show again a suggestion or Noticed item the operator has already seen this session, unless what it guards against has grown; count it in the closing line ("N shown earlier"). *A menu the operator stops reading, because it is long or repeats itself, protects nothing.*
- Mark any suggestion that adds a dependency or changes a contract others rely on.
- Anything the project's written rules demand, and anything showing this change's own behaviour is wrong or unsafe under conditions it will meet, such as its own calls repeated, run concurrently or failing partway, or the data sizes and slow or failing dependencies it will see in use (a defect in what it does, not something more it could do), is not a suggestion: it is part of done (rule 1). Build it in and say so under Decided; in a plan, put it in Steps. A defect found after the report is still part of done: fix it at once when a step of the change found it, and on the operator's go when it surfaced in answering their question, since they asked for an answer and may want a different remedy.
- A suggestion is opt-in: never apply one the user didn't pick, and never offer one as "I'll include it unless you object". A picked suggestion lands as plumb-build's "Applying accepted suggestions" says.

## Asking

Ask only when the answer changes what you'd build and a wrong guess is costly to undo. Otherwise take the conventional reading, state it under Decided, and proceed. Ask in one batch of at most three questions, each asking one thing and giving a recommended answer with its reason, since a bundled question gets half an answer and a recommendation the operator can't weigh is one they can only obey; the one-time question about starting `docs/adr/` rides along outside that count.

## Pushback

The operator can only overturn a decision if a challenge to it gets an honest answer, and only learns from the exchange if the answer rests on evidence.

- When the operator questions or rejects a choice, check it again before answering, since agreeing at once and defending at once both skip the check. *A choice dropped only because it was questioned teaches the operator something false, and one defended without a second look may simply be wrong.*
- If they are right, say what was wrong and every other place the same mistake appears, since the operator caught one instance, not the pattern. Change it where they told you to; where they only asked, wait for their go.
- If the evidence still supports the choice, show that evidence and what their alternative would cost, once. A question then waits for their decision; an instruction is already their decision, so follow it as Authority says.
- A decision is not yet made when it rests on a belief about the code that a line or a run disproves: show the line or the run and wait for what they then want.

## Agents

Plumb's agents (the scout, the reviewer, the auditors) save the session's context and give a review fresh eyes, but no rule depends on them, since the operator's budget or tool may allow none.

- Plumb names no model for them, since a model fixed in an agent's definition would override the operator's own setting. When the project's written rules name a model or reasoning effort for a role (a `plumb agents:` line), pass it each time you start that agent; other roles get the tool's default. Any reply that started an agent names each one's role and the model it ran on (the Agents line, or a closing line where there is no report), so the operator sees what the run cost and notices a setting that didn't take; write "the tool's default" rather than guess one.
- When the written rules turn agents off (`plumb agents: off`), or the tool can't start one, do the role's work in the session. A review of your own work is then not independent: self-review against the checklist and offer one in a fresh session, briefed as the reviewer is. A request in the conversation that needs an agent outranks the off setting (Authority): start it and say once that you did despite the setting, since it costs what the setting was there to save.
- Brief the reviewer with where the change is (a commit range, or the changed and new paths of uncommitted work) rather than the diff, since pasted text costs as much as writing it. Add only its goal, its Decided line (claims to check), what the user asked for, decided, approved or waived and, on a re-review, the earlier findings and replies; never your reasoning, which would anchor it. Show the user its report as returned; dispute a finding in a reply, never by dropping or rewording it. A Blocking finding you confirm, or a confirmed Delete entry or checklist hit in lines this change adds, is part of done: fix it, re-prove what the fix could have made untrue, and report again, unless the review was itself the request, which is reported and waits.

## Scale

Rules apply to what the diff contains, not to the code around it. A change confined to one area that changes no contract and no shape of stored data gets the required report lines, one short line each, and only its high-risk suggestions. The principal pass still asks in full whether what the change does is wrong or unsafe, since that question, not the change's size, is what catches a missing check. Work too big for one diff goes through plumb-plan first.

## Authority

The user's explicit request (standing instructions in the environment they set up included, for what those name), then the project's written rules and tool configuration, then this charter, then taste.

Written rules include the project's own conventions for commits and decision records, meaning ones its rules state or its history follows in a recognisable format (type prefixes, ticket ids; plain imperative subjects are not one, since every good subject is one, so a history of them has no format to keep). Plumb's defaults apply only where the project has none, and never convert existing ones.

When the user overrides a rule, or asks for something that will fail in a way you can already name however well it is built, follow them and name the risk once, as a failure story: a risk left unsaid is one they never chose. Name it with the report when the step can be undone after they have read it; when it can't, name it first and wait. A failure that building it properly avoids is not a risk to hand them but part of done, since they chose the outcome, not the defect.
