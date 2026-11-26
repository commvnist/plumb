# 9. What plumb commits or posts reads as the operator's work

## Status

Accepted. Amended by [ADR 11](0011-pull-request-comments-in-the-operators-own-voice.md): comments on a pull request speak in the operator's own voice.

## Context

commvnist wants what plumb commits or posts to be indistinguishable from the operator's own work (2026-11-17, tightened 2026-11-18): tools add co-author trailers and "Generated with" footers by default, and agents write "I" and "we".

## Decision

Everything plumb commits or posts (code comments, commits, pull requests, review comments) is in a neutral technical voice: no first person, and nothing that credits, implies or mentions AI authorship or use. Commits use the configured git identity, never one the agent sets. Replies to the operator in the session are not filtered. Charter rule 19 states it; `hooks/check-commit.sh` checks commits and `gh` pull request and issue text after the fact.

## Consequences

- A tool's own attribution setting fights this on every commit; the README tells operators to turn it off at the source.
- The hook is a backstop, matched by pattern: it misses text posted by other means.
