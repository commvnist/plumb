---
type: llm
---
Pass only if all hold:
- test_dict_has_keys is marked for deletion (it tests Python, not billing).
- test_build_totals_again is marked as a duplicate to merge or delete.
- test_build_matches_formula is flagged for computing the expected value the way the code does.
- The missing tests named include proration.credit_cents (rounding down, the days_in_period guard), ranked by risk.
- Findings are ranked, concrete, and nothing was changed.
