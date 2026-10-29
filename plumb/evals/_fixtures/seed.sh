#!/bin/bash
# Seeds the eval workspace (the current directory) with a fixture repository.
# Usage from a case's scaffold.sh: . "$(dirname "$0")/../_fixtures/seed.sh" <fixture>
set -euo pipefail
python3 "$(dirname "${BASH_SOURCE[0]}")/make.py" "$1" .
git config user.email dev@example.com
git config user.name Dev
