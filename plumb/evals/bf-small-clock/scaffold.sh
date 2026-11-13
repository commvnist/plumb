#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

cat > tests/test_cart.py <<'PY'
import unittest
from decimal import Decimal

from shop.cart import Cart


class CartTest(unittest.TestCase):
    def test_coupon_applies_above_minimum(self):
        cart = Cart()
        cart.add("mug", Decimal("30"), 2)
        cart.coupon = {"percent": 10, "minimum": Decimal("50")}
        self.assertEqual(cart.total(), Decimal("54.00"))


if __name__ == "__main__":
    unittest.main()
PY
git add -A && git commit -qm "test: coupon minimum"
