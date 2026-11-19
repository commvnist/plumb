# 10. Skill text and its eval case live and die together

## Status

Accepted

## Context

Plumb's skills are prompts, so wording is behaviour, and every word is loaded in every session. The 0.11.0 trim cut the text from about 15,700 words to 2,300 while the eval suite scored the same, which showed the suite couldn't see much of what the text did. A November 2026 review found why: single runs inside the noise, evidence graded from the agent's own reply, and cases that can't reach harm that happens across diffs, releases or live systems.

## Decision

A clause lands with a case that fails without it and passes with it, each arm run at least three times, and each case names the text it guards (`GUARDS` in `plumb/evals/_fixtures/write_cases.py`, checked by `scripts/check_refs.py`). A clause whose case passes as often without plumb goes. A clause that guards against harm a diff can't revert (lost data, a leaked secret, a step on a live system) goes only if its case passes without plumb in at least three runs on the weakest model plumb supports. A rewording that adds no requirement and no words lands when the cases touching it still pass.

## Consequences

- Trims can't silently drop a guarded clause: CI fails until its case changes with it.
- Eval runs cost three times as much as before.
- Harm the sandbox can't produce is judged on weaker evidence, which is why its bar for removal is higher.

## Update, 2026-11-19

A second review found two standards in use: additions were judged at three runs per arm while a comparable drop was called noise at six. One rule now judges both, fixed before results are read: 0/3 against 3/3 decides; a disputed decision runs each arm to six and decides at Fisher's exact p ≤ 0.1; anything else leaves the text as it is. "The weakest model plumb supports" is the floor model, the smallest model the tool offers, and harm cases stay in the suite even when a stronger model passes them without plumb. Restoring a harm case does not restore the text it once guarded; that text returns only if the case is red on the floor model without it.
