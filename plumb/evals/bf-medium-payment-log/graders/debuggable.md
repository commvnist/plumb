---
type: llm
focus: {source: file, path: app/handlers/payments.py}
---
This is app/handlers/payments.py after the change. Pass if a failed payment is logged with the
order id and the reason it failed (the decline, or the exception's type or message), so support
can tell attempts apart and see why each failed.
