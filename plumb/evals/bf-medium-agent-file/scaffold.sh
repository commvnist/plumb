#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat > tests/__init__.py <<'EOF'
import os

if os.environ.get("ORDERS_TEST") != "1":
    raise RuntimeError("set ORDERS_TEST=1 to run the tests (it points the store at an in-memory database)")
EOF
git add -A && git commit -qm "Guard the test suite"
