#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

python3 - <<'PY'
p = "shop/cart.py"
old = "    def remove(self, name):\n"
new = ('    def names(self):\n'
       '        \"\"\"The names of the items in the cart, in the order they were added.\"\"\"\n'
       '        return list({i["name"] for i in self.items})\n\n' + old)
s = open(p).read().replace(old, new)
open(p, "w").write(s)
PY
cat > tests/test_cart.py <<'EOF'
import unittest
from decimal import Decimal

from shop.cart import Cart


class CartTest(unittest.TestCase):
    def test_names_in_the_order_added(self):
        cart = Cart()
        cart.add("pen", Decimal("1"))
        cart.add("mug", Decimal("5"))
        self.assertEqual(cart.names(), ["pen", "mug"])


if __name__ == "__main__":
    unittest.main()
EOF
git add -A && git commit -qm "feat: list the names in a cart"
