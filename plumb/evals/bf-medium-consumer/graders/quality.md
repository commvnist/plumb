---
type: llm
---
Pass only if all hold:
- The consumer is safe on redelivery (the broker delivers at least once, as the shipping consumer documents): a duplicate event doesn't fail or change state twice, and an unknown order is handled as the shipping consumer handles it.
- It follows the shipping consumer's conventions (store.set_status, one log event per message with an outcome).
- A test covers redelivery, and tests were run and passed.
- The final reply ends with plumb's report or an equivalent receipt that includes a line stating the choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line quoting a command that was actually run with its result.
