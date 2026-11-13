---
type: llm
focus: {source: file, path: tests/test_cart.py}
---
This is tests/test_cart.py after the change. Pass if every test gives the same result whatever
day it runs on: the tests control the current time (pass it in, inject a clock, or patch it) or
place dates relative to a time the test controls. Fail if any test compares a fixed calendar
date (such as 2030-01-01) or the real current date against the real clock, because such a
test changes result as days pass.
