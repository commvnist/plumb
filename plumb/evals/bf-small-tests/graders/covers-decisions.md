---
type: llm
focus: {source: file, path: tests/test_cart.py}
---
This is the test file the agent wrote for shop/cart.py. Pass if its tests cover merging a repeated
item, rejecting a quantity below 1, and the coupon applying on one side of its minimum and not the
other, calling Cart's public methods and asserting outcomes. A test at exactly the minimum is not
required: the docstring and the code disagree there.
