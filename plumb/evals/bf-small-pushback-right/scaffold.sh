#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

cat >> shop/pricing.py <<'PY'


def split_evenly(amount, people):
    # Splits a bill into equal shares.
    return round(float(amount) / people, 2)


def unit_price(total, quantity):
    return round(float(total) / quantity, 2)
PY
git commit -qam "Add bill splitting and unit prices"
