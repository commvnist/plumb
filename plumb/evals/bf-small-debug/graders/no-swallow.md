---
type: llm
focus: {source: file, path: shop/pricing.py}
---
This is shop/pricing.py after the change. Pass if parse_price never hides a bad input: it doesn't
catch an error to return a default value or None. Catching an error only to raise a clearer one
(with the input and the original error chained) is fine.
