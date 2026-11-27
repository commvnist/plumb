---
name: plumb-jira
description: Writes issues and comments in plumb's format, in Jira or any tracker: any issue type (bugs, stories, tasks, epics, spikes, tests, incidents, changes), comments of every kind, edits, links and transitions. Use for "file a ticket", "create a Jira issue", "open a GitHub issue", "open a bug for this", "comment on PROJ-123", "update the ticket", "post progress to Jira", "post an update on the PR", "move it to done", or any write to a work item.
---

# Plumb: Jira and other trackers

An issue outlives the work that raised it: its reader arrives later with only the issue, so each one, and each comment, reads whole without the conversation that produced it.

Writing to a tracker notifies people. Create, comment, edit, link, assign, mention or transition only on an instruction to do that specific thing, on an item the operator's own words name or that this work created. Before creating, search for the issue already filed and add to it instead; one problem per issue. A vulnerability goes where the project takes private reports, never into a public issue unless the operator, told that it discloses the hole, still asks. Fields that rank or schedule the work (priority, sprint, fix version, assignee, estimate) are the team's call: set them only when told, and state the impact that informs them.

Before writing, read what the write depends on, never learning it by a trial write: the project's issue types, required fields, components and labels as they exist, never invented; for an edit, the field as it stands, since a write replaces the whole field, so carry over every part you weren't asked to change (another person's text, an embedded image, a link). Add to another person's description with a comment unless told to rewrite it.

Write in the markup the channel renders, learned from the tool or the instance, never assumed (a tool that converts Markdown, ADF for the Cloud REST API v3, wiki markup for v2 and Data Center), and read the item back once to see it rendered.

## The format

Each issue type is one of the kinds below. Use the type the operator names, in plain words too ("a task" is a Task), over the one whose kind seems to fit better; else the one whose kind fits the work, and where it is missing, the project's nearest, keeping the kind's shape.

- **Summary:** short, and what a person searching would type, naming where; never a commit subject. A defect names the symptom and what triggers it; a need, the outcome its users get; work, the change it makes, in the imperative, by its effect, naming the mechanism when the mechanism is the work ("Retry failed uploads in the nightly export"); a container, its outcome; a test, the behaviour it checks; a question, the question; an incident, the impact now; a problem, the recurring failure; a change, what changes where.
- **Description,** under short headings, in this order, leaving out a part with nothing known rather than holding its place:
  - a defect (bug, a defect found in testing): what happens and whom it affects; how often, and where (version or commit, environment), with the last version without it when known; steps to reproduce from a clean start; expected against actual; the evidence (the command and its output); a workaround, when known; a cause no run has proved, marked as suspected, kept apart from what was observed.
  - a need (story, feature, improvement): the problem and who has it, not an implementation; what shows it done, specific to this item rather than the team's definition of done, each criterion checkable by someone else; what is out of scope. A story is one slice its users can use; one too large to finish soon is an epic.
  - work (task, sub-task, technical debt): why it is needed, for debt the cost it carries now; what shows it done; what is out of scope. A sub-task says only what its parent doesn't.
  - a container (epic, initiative): the outcome and the measure that shows it reached; what is out of scope; its work is its child issues, linked as children and each whole without it, not a list kept in its text.
  - a question (spike, research): the question, why it matters, what is already known, and what would settle it; done is an answer recorded on the issue within the time the team allows, with its evidence and the work it implies, and its code is not shipped.
  - a test (test case): the requirement it checks, linked; the state it starts from; steps, each with its expected result. A test run (execution, plan) names the build it ran on and each case's result, and links each failure's defect.
  - operations (incident, problem, change): an incident, the impact now and since when, the current state, any workaround, and when the next update comes, then a timeline with times and their zone; a problem, the incidents it explains, the root cause and its evidence, the workaround until the fix, the fix; a change, what changes and why, the risk, how it rolls out, what shows it worked, the way back, and its window.
- **A comment** reads whole for someone who missed the rest and does one job: an update, what the work changed, read from the work itself (the commit, the diff, the run) rather than the request, a link to that change, then what happens next, ending with its last fact; a blocker, what blocks, who can clear it and what is needed from them; a question, one question with what it takes to answer it; a handoff, the state, what is left and where the work is; a review or test result, the verdict, the build or commit it ran on, the evidence, and the defects it filed; a decision reached elsewhere, what was decided, by whom and what it changes here; a reopen, what is still wrong and where it was seen.
- **A transition** that closes an issue sets the resolution and says why: the change that resolved it and the evidence it works (a test or run that shows it, run now if none is on record), or the reason it won't be done.
- **Links:** a pull request or commit by its URL; a related issue as the tracker's own link, in Jira one whose kind says how they relate.

Report each item written with its key and URL. When something can't be sent, give the complete text in the markup the instance renders, ready to paste.
