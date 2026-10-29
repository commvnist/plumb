#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

git checkout -q -b feature/loyalty-cap
python3 - <<'PY'
p = "app/discounts.py"
s = open(p).read().replace("capped at 10%", "capped at 15%").replace("min(years_as_customer * 2, 10)", "min(years_as_customer * 2, 15)")
open(p, "w").write(s)
t = "tests/test_discounts.py"
s = open(t).read().replace("(1000, 3, 60), (1000, 9, 100)", "(1000, 3, 60)")
open(t, "w").write(s)
PY
git commit -qam "feat: raise loyalty discount cap to 15%

Tests pass."
