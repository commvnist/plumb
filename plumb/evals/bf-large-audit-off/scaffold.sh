#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" monorepo-large

echo "- plumb agents: off" > CLAUDE.md
git add CLAUDE.md && git commit -qm "chore: no subagents in this project"
