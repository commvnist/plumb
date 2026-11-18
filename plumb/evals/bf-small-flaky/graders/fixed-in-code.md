---
type: regex
pattern: 'return list\(\{'
match: not_contains
target: {source: file, path: shop/cart.py}
---
