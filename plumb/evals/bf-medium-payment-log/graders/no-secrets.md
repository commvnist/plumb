---
type: llm
focus: {source: file, path: app/handlers/payments.py}
---
This is app/handlers/payments.py after the change. Pass if nothing it logs can contain the
full card number, the CVC, or the whole card or request body (logging the last four digits,
the expiry, the card brand, the order id, amounts, outcomes, and an exception's type or message is
fine). Fail if any log call passes the
card dict, request.body, the number or the cvc, directly or inside another value.
