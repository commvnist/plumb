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
git commit -qam "feat(pricing): add total_with_tax

Checkout needs prices with sales tax, rounded to the cent like every
other price."
git remote add origin https://github.com/example-shop/shop.git
