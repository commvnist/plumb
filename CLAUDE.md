# plumb

- Gate every change to plumb's skill, agent or hook text with the fast eval tier: `python3 plumb/evals/_fast/run.py --dry-run` first, then without `--dry-run` (see `plumb/evals/README.md`). Run the whole suite only when it says the selection covers most of it, or the operator asks: replayed over the last 16 changes to the text, the median selection was a fifth of the cases.
- Agent models in evals: Haiku 5.5 and Sonnet 5.5, kept apart; the strongest model only as judge.
- How a change lands, is checked and is released: `CONTRIBUTING.md`.
