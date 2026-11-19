#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

cat > pyproject.toml <<'EOF'
[project]
name = "shop"
version = "1.2.0"
EOF
cat > CHANGELOG.md <<'EOF'
# Changelog

## 1.2.0

- Prices can be parsed from text with `parse_price`.
EOF
git add -A && git commit -qm "chore(release): 1.2.0" && git tag v1.2.0
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
sed -i 's/cleaned = text.strip().lstrip("\$")/cleaned = text.strip().lstrip("$").replace(",", "")/' shop/pricing.py
grep -q 'replace(",", "")' shop/pricing.py
git commit -qam "fix(pricing): accept thousands separators in typed prices"
