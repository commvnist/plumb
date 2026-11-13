#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" shop-small

cat > pyproject.toml <<'TOML'
[project]
name = "shop"
version = "1.4.0"
requires-python = ">=3.9"
TOML
mkdir -p .github/workflows
cat > .github/workflows/test.yml <<'YML'
name: test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.9"
      - run: python3 -m unittest
YML
git add -A && git commit -qm "build: package metadata and CI"
