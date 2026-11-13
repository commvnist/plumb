---
type: llm
focus: {source: file, path: app/discounts.py}
---
This is app/discounts.py after the change. The business rule is "2% off per full year as a
customer, capped at 10%". Pass if, after the change, that rule (the 2-per-year rate and the
10% cap) is written in exactly one place, and both the existing cents calculation and the new
percentage are derived from it. Fail if the rate or the cap is typed out twice, for example a
new function that repeats min(years * 2, 10) beside the old one that still has its own copy.
