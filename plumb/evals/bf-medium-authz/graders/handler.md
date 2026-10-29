---
type: llm
focus: {source: file, path: app/handlers/invoices.py}
---
Pass if the new single-invoice handler checks that the invoice belongs to the caller,
returns not-found for a missing id, and logs an event the way the neighbouring handlers do.
