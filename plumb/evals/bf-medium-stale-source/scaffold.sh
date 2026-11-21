#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

mkdir -p vendor/pricing-api
cat > vendor/README.md <<'EOF'
Copies of other teams' contracts, refreshed by hand. Each folder's SYNCED file says what it was copied from.
EOF
cat > vendor/pricing-api/SYNCED <<'EOF'
source: git.example.com/pricing/pricing-api docs/quote.md
commit: 3f2c1ab
synced: 2026-06-02
EOF
cat > vendor/pricing-api/quote.md <<'EOF'
# GET /quotes/{sku}

Returns a quote for one unit of the SKU.

| field | type | meaning |
|---|---|---|
| sku | string | the SKU asked for |
| amount_cents | integer | price of one unit |
| tax_cents | integer | tax on one unit |
| expires_at | string | RFC 3339 time after which the quote is void |
EOF
git add -A && git commit -qm "docs: copy the pricing API's quote contract"
