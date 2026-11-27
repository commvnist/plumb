# 13. Comments on a pull request are in the neutral voice

## Status

Accepted. Supersedes [ADR 11](0011-pull-request-comments-in-the-operators-own-voice.md).

## Context

ADR 11 made a comment on a pull request the one artifact written in the operator's first-person voice, so that a review comment would not read as a bot's. In use, that default put words in the operator's mouth they had not chosen, and split one voice rule into two. commvnist decided on 2026-11-27 that a comment on a pull request follows ADR 9 like everything else, and that a comment in the operator's own voice is something the operator asks for, text by text.

## Decision

A comment on a pull request (a review, a line comment, a reply) is in the neutral technical voice of ADR 9: impersonal, no first person, nothing on how it was produced. Where the operator asks for their own voice for a given text, that text is written so, and still mentions nothing of how it was produced. `hooks/check-commit.sh` flags first person in a pull request comment again, with the note it gives any post: reword it unless the operator asked for or approved that wording.

## Consequences

- One voice rule covers everything plumb commits or posts; the hook no longer tells comments apart from other posts.
- A comment the operator asked to be in their voice is still flagged by the hook, which can't see the ask; the note's "unless the operator asked for" clause covers it.
- The `review-voice` eval checks that line comments are neutral by default; `review-voice-asked` checks that an explicit ask still gets the operator's voice.
