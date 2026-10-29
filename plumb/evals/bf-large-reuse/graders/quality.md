---
type: llm
---
Pass only if all hold:
- It reuses common.throttle.RateLimiter rather than writing a new limiter, and follows the search API's pattern (429 response, a rate_limited log outcome).
- Both billing handlers are limited, and a test proves the limit (seen failing when the limit is wrong); tests were run and passed.
- Nothing outside the billing service was changed.
- The final reply ends with plumb's report or an equivalent receipt that includes a line stating the choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line quoting a command that was actually run with its result.
