#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

git checkout -q -b fix/auth-note
printf '\n# Checked by the gateway too.\n' >> app/auth.py
git commit -qam "fix: note the gateway check"
