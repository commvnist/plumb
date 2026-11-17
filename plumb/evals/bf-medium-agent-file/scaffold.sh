#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat > tests/__init__.py <<'EOF'
import os

if os.environ.get("ORDERS_TEST") != "1":
    raise RuntimeError("tests refuse to run without ORDERS_TEST=1 (they reset the shared clock)")
EOF
git add -A && git commit -qm "Guard the test suite"
