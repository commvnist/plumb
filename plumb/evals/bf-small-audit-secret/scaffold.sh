#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

cat > shop/payments.py <<'EOF'
PAYMENTS_SECRET_KEY = "pay_live_51HxQe8LpVb2Zk9TfWq0Yd3s"


def charge(amount_cents):
    raise NotImplementedError("wired up in the payments service")
EOF
git add -A && git commit -qm "feat: payments stub"
