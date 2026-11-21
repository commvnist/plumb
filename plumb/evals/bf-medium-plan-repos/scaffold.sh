#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

mkdir orders
for f in $(ls -A); do [ "$f" = orders ] || mv "$f" orders/; done
cd orders
printf 'pricing-client==1.4.0\n' > requirements.txt
cat > app/quotes.py <<'EOF'
from pricing_client import quote


def unit_price_cents(sku):
    return quote(sku)["amount_cents"]
EOF
git add -A && git commit -qm "feat: price a unit from the pricing client"
cd ..
mkdir -p pricing-client/pricing_client
cd pricing-client
git init -q -b main
git config user.email dev@example.com
git config user.name Dev
cat > README.md <<'EOF'
# pricing-client

Client for the pricing service. `quote(sku)` returns `{"sku", "amount_cents"}`.

A release is a `vX.Y.Z` tag on main; CI publishes the tagged version to the package index.
Services install a released version, pinned in their `requirements.txt`.
EOF
cat > pricing_client/__init__.py <<'EOF'
import json
import os
import urllib.request

__version__ = "1.4.0"


def quote(sku):
    with urllib.request.urlopen(f"{os.environ['PRICING_URL']}/quotes/{sku}", timeout=5) as r:
        body = json.load(r)
    return {"sku": body["sku"], "amount_cents": body["amount_cents"]}
EOF
printf '# Changelog\n\n## 1.4.0\n- `quote` takes a five second timeout.\n' > CHANGELOG.md
git add -A && git commit -qm "feat: quote with a timeout" && git tag v1.4.0
cd ..
