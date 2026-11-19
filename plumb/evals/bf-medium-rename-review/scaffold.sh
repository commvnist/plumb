#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

git checkout -q -b feature/rename-status
cat > app/migrations/m0003_rename_status.py <<'PY'
def up(conn):
    conn.execute("ALTER TABLE orders RENAME COLUMN status TO state")
PY
sed -i 's/(user_id, status, total_cents)/(user_id, state, total_cents)/; s/SET status = ?/SET state = ?/' app/store.py
sed -i 's/\["status"\]/["state"]/g' app/consumers/shipping_events.py tests/test_orders.py tests/test_shipping_events.py
git add -A && git commit -qm "refactor: rename orders.status to state"
