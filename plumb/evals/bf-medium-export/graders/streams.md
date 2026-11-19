---
type: llm
focus: {source: file, path: app/exports.py}
---
This is app/exports.py after the change. Pass if it writes invoices as it reads them (iterating
the cursor, or fetching in batches), so memory stays flat however many invoices there are. Fail if
it loads every invoice into a list first (fetchall, a list comprehension over all rows, or a store
function that returns them all).
