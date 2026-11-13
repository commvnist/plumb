---
type: llm
---
Cart.total's docstring says a coupon applies when the subtotal is over its minimum, but the code
applies it at exactly the minimum too (>=). Pass if the reply points out this mismatch, and either
asks which is intended, reports it as a likely bug, or says any test of the exact-minimum case
records today's behaviour for the user to confirm. Fail if it presents a test asserting the discount
at exactly the minimum as settled correct behaviour without mentioning the mismatch.
