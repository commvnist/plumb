#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

python3 - <<'PY'
p = "shop/pricing.py"
s = open(p).read()
s = s.replace('''def format_price(amount):
    return "$" + str(_round_cents(amount))''', '''def _legacy_round(amount):
    return amount.quantize(Decimal("0.01"))


def format_price(amount):
    return "$" + str(_legacy_round(amount))''')
open(p, "w").write(s)
t = "tests/test_pricing.py"
s = open(t).read().replace('''

if __name__''', '''
    def test_legacy_round_keeps_two_places(self):
        self.assertEqual(pricing._legacy_round(Decimal("2.5")), Decimal("2.50"))


if __name__''')
open(t, "w").write(s)
PY
git commit -qam "Format prices with the legacy rounding"
