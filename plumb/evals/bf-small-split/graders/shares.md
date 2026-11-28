---
type: llm
focus: {source: file, path: shop/pricing.py}
---
This is shop/pricing.py after the change. Judge split_bill's behaviour, not its style. Pass only
if both hold:
- The returned amounts always add up exactly to the amount, to the cent: leftover cents go to some
  of the people (for example 100.00 split 3 ways gives 33.34, 33.33 and 33.33), rather than every
  share being rounded the same way.
- A people count below 1 is rejected with a clear error (such as ValueError), rather than
  dividing by zero or returning negative or empty shares.
