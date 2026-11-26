# 11. Comments on a pull request speak in the operator's own voice

## Status

Accepted. Amends [ADR 9](0009-artifacts-in-the-operators-voice.md).

## Context

ADR 9 put everything plumb commits or posts in a neutral, impersonal voice. A review comment is different from a commit or a description: it is one person talking to another at a line of code, and an impersonal comment there reads as a bot's, which is the opposite of what ADR 9 wants. commvnist set the rule on 2026-11-26: the neutral voice and the absence of any mention of AI are fixed, except that comments on a pull request may speak as the operator, reading as naturally human.

## Decision

A comment on a pull request (a review, a line comment, a reply to review feedback) is written as the operator would write it to a colleague, first person where natural, with nothing in it that reads as generated. Everything else plumb commits or posts, a pull request's title and description included, stays impersonal. Nothing anywhere credits or mentions AI, agents, models, prompts or sessions behind the work. `hooks/check-commit.sh` no longer flags first person in a pull request comment, and still flags a credit line there.

## Consequences

- The hook tells a pull request comment from other posts by the `gh` command (`pr comment`, `pr review`, or the API's pull request comments and reviews). A pull request's conversation comment sent through the issues API looks like an issue comment, so it is still flagged for first person.
- Whether a comment reads as human is a judgement no pattern can check; it rests on the charter's wording.
