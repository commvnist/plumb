#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat > app/migrations/m0003_users.py <<'PY'
def up(conn):
    conn.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL, display_name TEXT NOT NULL,"
        " password_hash TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
PY
cat >> app/store.py <<'PY'


def create_user(conn, email, display_name, password_hash, created_at):
    cur = conn.execute(
        "INSERT INTO users (email, display_name, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (email, display_name, password_hash, created_at),
    )
    return cur.lastrowid


def get_user(conn, user_id):
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None
PY
git add -A && git commit -qm "feat: users table"
