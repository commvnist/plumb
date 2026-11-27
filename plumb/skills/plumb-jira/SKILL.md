---
name: plumb-jira
description: Writes issues and comments in plumb's format, in Jira or any tracker: new issues, progress updates, edits, links and transitions. Use for "file a ticket", "create a Jira issue", "open a GitHub issue", "open a bug for this", "comment on PROJ-123", "update the ticket", "post progress to Jira", "post an update on the PR", "move it to done", or any write to a work item.
---

# Plumb: Jira and other trackers

An issue outlives the work that raised it: its reader arrives later with only the issue, so each one, and each comment, reads whole without the conversation that produced it.

Writing to a tracker notifies people. Create, comment, edit, link, assign, mention or transition only on an instruction to do that specific thing, on an item the operator's own words name or that this work created. A vulnerability goes where the project takes private reports, never into a public issue unless the operator, told that it discloses the hole, still asks.

Before writing, read what the write depends on: the project's issue types, required fields, components and labels as they exist, never invented; for an edit, the field as it stands, since a write replaces the whole field, so carry over every part you weren't asked to change (another person's text, an embedded image, a link). Add to another person's description with a comment unless told to rewrite it.

Write in the markup the channel renders, learned from the tool or the instance, never assumed (a tool that converts Markdown, ADF for the Cloud REST API v3, wiki markup for v2 and Data Center), and read the item back once to see it rendered.

## The format

- **Summary:** the defect or need as someone searching would phrase it, naming where it happens and what goes wrong; never the fix, never a commit subject.
- **Description,** under short headings, in this order, leaving out a part with nothing to say:
  - for a defect: what happens and whom it affects; steps to reproduce from a clean start; expected against actual; the evidence (the command and its output, the version or commit it was seen on); a suspected cause only marked as unconfirmed, apart from what was observed.
  - for a need: the problem and who has it, not a solution; what shows it done, each criterion checkable by someone else; what is out of scope.
- **A comment or update:** what the work changed, read from the work itself (the commit, the diff, the run) rather than the request, its link, then what happens next or what is needed from whom.
- **Links:** a pull request or commit by its URL; a related issue as the tracker's own link, in Jira one whose kind says how they relate.

Report each item written with its key and URL. When something can't be sent, give the complete text in the markup the instance renders, ready to paste.
