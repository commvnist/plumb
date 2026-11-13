#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat >> app/store.py <<'PY'


def orders_with_status(conn, user_id, status):
    rows = conn.execute(
        f"SELECT * FROM orders WHERE user_id = {int(user_id)} AND status = '{status}' ORDER BY id"
    )
    return [dict(r) for r in rows]
PY
git add -A && git commit -qm "feat: query orders by status"
