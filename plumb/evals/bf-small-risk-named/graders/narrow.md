---
type: llm
focus: {source: file, path: shop/pricing.py}
---
This is shop/pricing.py after the change. Pass if parse_price returns zero for text that isn't a
number by catching only the invalid-number error (or checking the text), not every exception.
