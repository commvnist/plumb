#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

sed -i 's/ORDER_STATUSES = ("pending", "paid", "shipped", "cancelled")/ORDER_STATUSES = ("pending", "on_hold", "paid", "shipped", "cancelled")/' app/store.py
git commit -qam "feat: orders can be put on hold by support"
