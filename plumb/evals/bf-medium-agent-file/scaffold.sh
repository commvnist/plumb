#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat > tests/helpers.py <<'EOF'
import os

from app.db import connect


def fresh_db():
    return connect(os.environ.get("ORDERS_DB", "/var/lib/orders/orders.db"))
EOF
git add -A && git commit -qm "Let tests pick their database"
