---
type: llm
focus: {source: file, path: shop/cart.py}
---
This is shop/cart.py after the change. Pass if the expiry check can be given the time it
compares against (a parameter, an injectable clock, or a single module-level function a test
can replace), and the boundary is decided on purpose (whether a coupon is still valid on its
expiry date is clear from the code or a comment). Fail if the comparison reads the real clock
inline with no way for a caller or test to set it.
