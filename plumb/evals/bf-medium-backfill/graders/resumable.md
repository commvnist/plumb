---
type: llm
focus: {source: file, path: scripts/backfill_totals.py}
---
This is scripts/backfill_totals.py. Pass only if both hold:
- It works through the orders in bounded batches, committing each, rather than one transaction or
  one query over all 40 million orders.
- Killed part way and run again, it ends in the same result: each update sets the total from the
  invoices (never adds to it), and a rerun either skips what is done or redoes it harmlessly.
