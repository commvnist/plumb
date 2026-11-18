#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

echo "- plumb agents: reviewer haiku low" >> CLAUDE.md
git commit -qam "chore: choose the reviewer's model"
