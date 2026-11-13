#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

git checkout -q -b feature/tax
python3 - <<'PY'
p = "shop/pricing.py"
s = open(p).read()
s += '''

def total_with_tax(amount, tax_percent):
    # Adds sales tax, rounded to the cent.
    return _round_cents(amount * (Decimal(100) + Decimal(tax_percent)) / Decimal(100))
'''
open(p, "w").write(s)
PY
git commit -qam "feat(pricing): add total_with_tax"
python3 - <<'PY'
p = "shop/cart.py"
s = open(p).read().replace('''    def item_count(self):
        return sum(i["quantity"] for i in self.items)

''', '')
open(p, "w").write(s)
PY
git commit -qam "feat(cart)!: drop Cart.item_count

BREAKING CHANGE: callers count items themselves from Cart.items."
