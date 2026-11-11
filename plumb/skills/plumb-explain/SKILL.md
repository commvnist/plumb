---
name: plumb-explain
description: Walks the operator through code, a diff or a decision until they could defend it in review, covering what it does, traced through one real case, why it is built this way, and where it could be wrong. Changes nothing. Use for "explain this", "walk me through", "how does this work", "why did you do it this way", "what does this diff do", "I don't follow".
---

# Plumb: explain

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

An explanation exists so the operator can vouch for the code and overturn what is wrong in it. It is finished when they could explain it to someone else, not when everything about it has been said.

## Steps

1. **Take the scope and depth from the question.** A line, a function, a diff or a decision: answer what was asked, pitched at what their words and the code they already work in show they know. Ask what they know only when the answer would change the whole explanation.
2. **Read it before explaining it.** Read the code and what it calls, and for work from this session re-read the diff, since an explanation from memory describes what you meant to write (charter rule 14). For a why, read the history, the decision records and the report's Decided line. A reason you can't find is given as unknown, or as your inference and marked so, never as fact. *An invented reason gets repeated as the project's own.*
3. **Lead with the point.** One or two sentences: what it does for its caller, and the one idea that makes it work.
4. **Trace one real case.** Follow one concrete input through the code to its outcome, by file:line, then the case where the path differs (an error, an edge). Run it where that is cheap and affects nothing, and say which parts you ran and which you read (charter rule 13). *A reader keeps a traced example long after a description has gone.*
5. **Give the reasons.** For each choice a reader would question: what was chosen, the alternative, and what the alternative would cost here. Name the technique or principle in a word or two, and say in a line what any term the codebase doesn't otherwise use means, so they can look it up and recognise it next time.
6. **Say where it could be wrong.** What the code assumes, what you didn't verify, and the place you would look hardest as its reviewer. A defect or a better choice that the explaining exposed is reported and its fix offered; in work from this session that isn't shipped, say that it is part of done (charter rule 1) and fix it on their yes.
7. **Hand them something to try.** One check they can run themselves that would show the explanation is true: a command, or a line to change and the test that then fails. *Trying it is what turns being told into knowing.*

## Output

```
In short:     <what it does and the idea that makes it work>
Walkthrough:  <one case traced by file:line, then where the path differs; what was run and what was read>
Why this way: <choice — alternative — what the alternative would cost — (technique or principle)>, one per line
Not sure:     <assumptions, what wasn't verified, reasons that are inference — or "nothing">
Look hardest: <the place a mistake would cost most, and what to check there>
Try it:       <one check they can run>
Noticed:      <defects or better choices the explaining exposed, each with the fix offered — or omit>
```

A question about one line or one choice gets the lines that answer it, not the whole template.

## Rules

- Change nothing: no edits, and no files beyond what a run leaves ignored. A fix is offered, and lands as plumb-build applies accepted suggestions.
- Explain what is there, not what you would have written. An improvement is a suggestion, by the charter's menu rules.
- Point at code by file:line instead of quoting it at length, and go line by line only when asked. An explanation longer than the code it explains has usually stopped explaining.
- Correct a wrong belief plainly, as the charter's Pushback says, and never soften what the code does to agree with the question.
- No quiz and no talking down. The operator decides when they have understood.
