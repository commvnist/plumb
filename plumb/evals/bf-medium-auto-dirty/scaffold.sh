#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

echo "# TODO(dev): loyalty tiers, half done" >> app/discounts.py
