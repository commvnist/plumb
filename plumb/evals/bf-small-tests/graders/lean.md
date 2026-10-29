---
type: llm
target: {source: file, path: tests/test_cart.py}
---
This is the test file the agent wrote for shop/cart.py. Pass if it has at most about eight tests,
with no test of a trivial accessor on its own and no two tests that would catch the same break
(table-driven subtests count as one test).
