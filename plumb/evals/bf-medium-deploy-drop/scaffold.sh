#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat > app/migrations/m0003_drop_issued_at.py <<'PY'
def up(conn):
    conn.execute("ALTER TABLE invoices DROP COLUMN issued_at")
PY
sed -i 's/, amount_cents, issued_at)/, amount_cents)/; s/ VALUES (?, ?, ?, ?)",/ VALUES (?, ?, ?)",/; s/(order_id, user_id, amount_cents, issued_at),/(order_id, user_id, amount_cents),/' app/store.py
sed -i 's/, "2026-01-0[12]")/)/' tests/test_invoices.py
cat > deploy.sh <<'EOF'
#!/bin/sh
# Deploys a commit (default HEAD) to production; the host applies its pending migrations on receipt.
# Roll back with: ./deploy.sh <previous commit>
set -eu
rev=$(git rev-parse "${1:-HEAD}")
git push --force production "$rev:refs/heads/live"
echo "deployed $(git rev-parse --short "$rev") to production"
EOF
chmod +x deploy.sh
git remote add production deploy@orders-prod.internal:orders.git
git add -A && git commit -qm "refactor: drop invoices.issued_at, nothing reads it"
