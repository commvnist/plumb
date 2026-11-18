#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

python3 - <<'PY'
p = "shop/cart.py"
s = open(p).read().replace("    def total(self):\n", '    def total(self):\n        \"\"\"Applies the coupon when the subtotal is over the coupon minimum.\"\"\"\n')
open(p, "w").write(s)
PY
git commit -qam "Document when a coupon applies"
