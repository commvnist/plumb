#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

sed -i 's/min(years_as_customer \* 2, 10)/min(years_as_customer * 2, 12)/' app/discounts.py
