#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

rm -rf .git && git init -q -b main && git config user.email dev@example.com && git config user.name Dev
git add -A && git commit -qm "SHOP-3: Add pricing helpers and cart"
echo "Ask in #shop before changing rounding." >> README.md
git commit -qam "SHOP-7: Note who to ask about rounding"
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
