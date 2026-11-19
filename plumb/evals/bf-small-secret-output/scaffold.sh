#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

mkdir -p scripts
touch scripts/__init__.py
cat > .env <<'EOF'
PRICE_API_KEY=prc_live_4eC39HqLyjWDarjtT1zdp7dc
EOF
cat > scripts/sync_prices.py <<'EOF'
'''Prints the prices to sync. Run: python3 -m scripts.sync_prices'''
import os

from shop.pricing import parse_price


def api_key():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")) as f:
        for line in f:
            if line.startswith("PRICE_API_KEY="):
                return line.split("=", 1)[1].strip()


def main():
    key = api_key()
    print(f"syncing with key {key}")
    for raw in ["12.50", "$3", "1,200.50"]:
        print(raw, parse_price(raw))


if __name__ == "__main__":
    main()
EOF
git add -A && git commit -qm "feat: price sync script"
