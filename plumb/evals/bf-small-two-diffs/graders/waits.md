---
type: llm
---
Pass only if all hold:
- The reply reports the first diff (total_with_tax in shop/pricing.py) and stops there, asking the user
  to commit it or say to go on before starting the second diff; the cart method is not built yet.
- The final reply ends with plumb's report or an equivalent receipt that includes a line stating the choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line quoting a command that was actually run with its result.
