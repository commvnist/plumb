---
type: llm
focus: {source: file, path: app/handlers/shipping.py}
---
This is app/handlers/shipping.py after the change. Pass if, when the carrier call fails, the
handler logs an event that carries the order id and the cause of the failure (the exception, its
message, or the carrier's status), so support can see which quote failed and why. Fail if a
failure is logged with only a generic outcome and no cause, or not logged at all.
