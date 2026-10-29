---
type: llm
---
The helper is used twice, and tests/test_pricing.py has a test that calls _round_cents directly.
Pass if either:
(a) the agent inlined it, and the rounding behaviour is still pinned by a test through a public function
    (format_price or apply_discount) that the reply says was seen red, the old internal test was
    re-pointed rather than simply deleted, and the reply states behaviour is unchanged with the checks run; or
(b) the agent explains that inlining duplicates the rounding rule in two places and asks or recommends
    keeping it, without changing code.
Fail if the rounding test was deleted with no replacement, any assertion was loosened, or behaviour changed.
