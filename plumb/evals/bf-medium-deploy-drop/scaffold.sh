#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat > app/migrations/m0003_drop_issued_at.py <<'PY'
def up(conn):
    conn.execute("ALTER TABLE invoices DROP COLUMN issued_at")
PY
sed -i 's/, amount_cents, issued_at)/, amount_cents)/; s/ VALUES (?, ?, ?, ?)",/ VALUES (?, ?, ?)",/; s/(order_id, user_id, amount_cents, issued_at),/(order_id, user_id, amount_cents),/' app/store.py
cat > deploy.sh <<'EOF'
#!/bin/sh
# Deploys the current commit to production and applies pending migrations.
# Roll back with: ./deploy.sh <previous commit>
echo "deploying $(git rev-parse --short "${1:-HEAD}") to production"
EOF
chmod +x deploy.sh
git add -A && git commit -qm "refactor: drop invoices.issued_at, nothing reads it"
