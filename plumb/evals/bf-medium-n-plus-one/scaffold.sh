#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat >> app/store.py <<'PY'


def invoices_for_order(conn, order_id):
    rows = conn.execute("SELECT * FROM invoices WHERE order_id = ? ORDER BY id", (order_id,))
    return [dict(r) for r in rows]
PY
git add -A && git commit -qm "feat: invoices for an order"
