#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

mkdir -p scripts
cat > scripts/migrate_staging.sh <<'EOF'
#!/bin/sh
# Brings the staging database's schema up to date.
set -eu
: "${STAGING_DB:?set STAGING_DB to the staging database file}"
work=$(mktemp -d)
git fetch -q origin release
git archive origin/release app | tar -x -C "$work"
cd "$work"
python3 -c "import os; from app.db import connect; connect(os.environ['STAGING_DB'])"
EOF
chmod +x scripts/migrate_staging.sh
git add -A && git commit -qm "chore: script the staging schema update"
