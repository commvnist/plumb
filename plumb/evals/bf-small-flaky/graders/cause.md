---
type: llm
---
Pass only if the reply names the cause: names() builds a set, and a set of strings iterates in an
order that depends on per-process hash randomisation, so the order changes between runs. It backs
that with a run that fails on demand (for example with a fixed PYTHONHASHSEED), and the fix keeps
the order items were added (as the docstring promises) rather than loosening the test or adding a
retry or sleep.
