#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

echo "- plumb agents: off" >> CLAUDE.md
git commit -qam "chore: no subagents in this project"
