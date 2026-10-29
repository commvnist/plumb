#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

python3 - <<'PY'
p = "shop/pricing.py"
s = open(p).read()
s += '''

def total_with_tax(amount, tax_percent):
    # Adds sales tax, rounded to the cent.
    return _round_cents(amount * (Decimal(100) + Decimal(tax_percent)) / Decimal(100))
'''
open(p, "w").write(s)
t = "tests/test_pricing.py"
s = open(t).read().replace('''

if __name__''', '''
    def test_total_with_tax_rounds_half_up(self):
        self.assertEqual(pricing.total_with_tax(Decimal("10.05"), 10), Decimal("11.06"))


if __name__''')
open(t, "w").write(s)
PY
