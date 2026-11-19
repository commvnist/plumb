# 7. Reports carry no "Try it" line

## Status

Accepted

## Context

An early proposal added a line to every report telling the operator how to try the change themselves. commvnist declined it (2026-11-12): the Verified line already quotes what was run, and plumb-explain hands over a check when the operator wants to learn the code.

## Decision

The report has no "Try it" or live-verification line. Verified carries the evidence; plumb-explain carries the hands-on check.

## Consequences

- A review that proposes a "Try it" line is re-raising this; it needs a new argument.
- Operators who want to try a change themselves ask for it, or for a walkthrough.
