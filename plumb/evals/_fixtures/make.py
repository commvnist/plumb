"""Builds the seeded repositories plumb's eval cases start from.

Usage: python3 make.py <fixture> <dest>
Fixtures: shop-small, orders-medium, monorepo-large, todo-web, notifier.
Each one is written into <dest> and committed as a git repository with a
short history, so brownfield cases have real code, tests and log to read.
"""
import os
import subprocess
import sys
import textwrap

GIT = ["git", "-c", "user.email=dev@example.com", "-c", "user.name=Dev", "-c", "commit.gpgsign=false"]


def write(root, files):
    for path, body in files.items():
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full) or root, exist_ok=True)
        with open(full, "w") as f:
            f.write(textwrap.dedent(body).lstrip("\n"))


def commit(root, message):
    subprocess.run(GIT + ["add", "-A"], cwd=root, check=True)
    subprocess.run(GIT + ["commit", "-qm", message], cwd=root, check=True)


def init(root):
    os.makedirs(root, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)


# --- shop-small: a tiny pricing library -------------------------------------

SHOP_V1 = {
    "README.md": """
        # shop

        Pricing helpers for the shop. Run the tests with `python3 -m unittest`.
    """,
    "shop/__init__.py": "",
    "shop/pricing.py": '''
        from decimal import Decimal, ROUND_HALF_UP


        def parse_price(text):
            """Parses a price typed by a customer, such as "12.50" or "$3"."""
            cleaned = text.strip().lstrip("$")
            return Decimal(cleaned)


        def _round_cents(amount):
            return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


        def format_price(amount):
            return "$" + str(_round_cents(amount))


        def apply_discount(amount, percent):
            if not 0 <= percent <= 100:
                raise ValueError("percent must be between 0 and 100")
            return _round_cents(amount * (Decimal(100) - Decimal(percent)) / Decimal(100))
    ''',
    "shop/cart.py": '''
        from decimal import Decimal

        from shop.pricing import apply_discount


        class Cart:
            def __init__(self):
                self.items = []
                self.coupon = None

            def add(self, name, unit_price, quantity=1):
                if quantity < 1:
                    raise ValueError("quantity must be at least 1")
                for item in self.items:
                    if item["name"] == name:
                        item["quantity"] += quantity
                        return
                self.items.append({"name": name, "unit_price": unit_price, "quantity": quantity})

            def remove(self, name):
                self.items = [i for i in self.items if i["name"] != name]

            def item_count(self):
                return sum(i["quantity"] for i in self.items)

            def subtotal(self):
                return sum((i["unit_price"] * i["quantity"] for i in self.items), Decimal(0))

            def total(self):
                subtotal = self.subtotal()
                if self.coupon and subtotal >= self.coupon["minimum"]:
                    return apply_discount(subtotal, self.coupon["percent"])
                return subtotal
    ''',
    "tests/__init__.py": "",
    "tests/test_pricing.py": '''
        import unittest
        from decimal import Decimal

        from shop import pricing


        class PricingTest(unittest.TestCase):
            def test_parses_plain_price(self):
                self.assertEqual(pricing.parse_price("12.50"), Decimal("12.50"))

            def test_parses_dollar_sign(self):
                self.assertEqual(pricing.parse_price("$3"), Decimal("3"))

            def test_round_cents_rounds_half_up(self):
                self.assertEqual(pricing._round_cents(Decimal("2.345")), Decimal("2.35"))

            def test_discount_rejects_over_100(self):
                with self.assertRaises(ValueError):
                    pricing.apply_discount(Decimal("10"), 120)


        if __name__ == "__main__":
            unittest.main()
    ''',
}


def shop_small(root):
    init(root)
    write(root, SHOP_V1)
    commit(root, "Add pricing helpers and cart")
    write(root, {"CONTRIBUTING.md": """
        # Contributing

        - Run `python3 -m unittest` before every commit.
        - Money is always `Decimal`, never float.
    """})
    commit(root, "Add contributing notes")


# --- orders-medium: a small order service ------------------------------------

ORDERS = {
    "README.md": """
        # orders

        Order and invoice service. Handlers are plain functions taking a
        `Request` and returning a `Response` (see `app/http.py`). Storage is
        SQLite (`app/db.py`). Run the tests with `python3 -m unittest discover -s tests -t .`.
    """,
    "CLAUDE.md": """
        # Project rules

        - Every handler that returns a customer's data checks ownership with `require_owner`.
        - Schema changes go through `app/migrations/`, one numbered file each.
        - Log one event per handled request with `app.log.event`.
    """,
    "app/__init__.py": "",
    "app/http.py": '''
        class Request:
            def __init__(self, user_id, params=None, body=None):
                self.user_id = user_id
                self.params = params or {}
                self.body = body or {}


        class Response:
            def __init__(self, status, body=None):
                self.status = status
                self.body = body


        class Forbidden(Exception):
            pass


        class NotFound(Exception):
            pass
    ''',
    "app/auth.py": '''
        from app.http import Forbidden


        def require_owner(request, resource):
            """Raises Forbidden unless the signed-in user owns the resource."""
            if request.user_id is None or resource["user_id"] != request.user_id:
                raise Forbidden()
    ''',
    "app/log.py": '''
        import json
        import sys


        def event(name, **fields):
            sys.stderr.write(json.dumps({"event": name, **fields}) + "\\n")
    ''',
    "app/db.py": '''
        import sqlite3

        from app.migrations import apply_all


        def connect(path=":memory:"):
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            apply_all(conn)
            return conn
    ''',
    "app/migrations/__init__.py": '''
        import importlib
        import pkgutil


        def apply_all(conn):
            """Applies each migration not yet recorded in schema_migrations, in name order."""
            conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY)")
            done = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}
            names = sorted(m.name for m in pkgutil.iter_modules(__path__) if m.name.startswith("m0"))
            for name in names:
                if name in done:
                    continue
                importlib.import_module(f"{__name__}.{name}").up(conn)
                conn.execute("INSERT INTO schema_migrations (name) VALUES (?)", (name,))
            conn.commit()
    ''',
    "app/migrations/m0001_orders.py": '''
        def up(conn):
            conn.execute(
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL,"
                " status TEXT NOT NULL, total_cents INTEGER NOT NULL)"
            )
    ''',
    "app/migrations/m0002_invoices.py": '''
        def up(conn):
            conn.execute(
                "CREATE TABLE invoices (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL,"
                " user_id INTEGER NOT NULL, amount_cents INTEGER NOT NULL, issued_at TEXT NOT NULL)"
            )
    ''',
    "app/store.py": '''
        ORDER_STATUSES = ("pending", "paid", "shipped", "cancelled")


        def create_order(conn, user_id, total_cents):
            cur = conn.execute(
                "INSERT INTO orders (user_id, status, total_cents) VALUES (?, 'pending', ?)",
                (user_id, total_cents),
            )
            return cur.lastrowid


        def get_order(conn, order_id):
            row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            return dict(row) if row else None


        def set_status(conn, order_id, status):
            if status not in ORDER_STATUSES:
                raise ValueError(f"unknown status {status!r}")
            conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))


        def orders_for_user(conn, user_id):
            rows = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id", (user_id,))
            return [dict(r) for r in rows]


        def create_invoice(conn, order_id, user_id, amount_cents, issued_at):
            cur = conn.execute(
                "INSERT INTO invoices (order_id, user_id, amount_cents, issued_at) VALUES (?, ?, ?, ?)",
                (order_id, user_id, amount_cents, issued_at),
            )
            return cur.lastrowid


        def get_invoice(conn, invoice_id):
            row = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
            return dict(row) if row else None


        def invoices_for_user(conn, user_id):
            rows = conn.execute("SELECT * FROM invoices WHERE user_id = ? ORDER BY id", (user_id,))
            return [dict(r) for r in rows]
    ''',
    "app/handlers/__init__.py": "",
    "app/handlers/orders.py": '''
        from app import log, store
        from app.auth import require_owner
        from app.http import NotFound, Response


        def get_order(conn, request):
            order = store.get_order(conn, int(request.params["id"]))
            if order is None:
                raise NotFound()
            require_owner(request, order)
            log.event("order.get", user_id=request.user_id, order_id=order["id"], outcome="ok")
            return Response(200, order)


        def list_orders(conn, request):
            orders = store.orders_for_user(conn, request.user_id)
            log.event("order.list", user_id=request.user_id, count=len(orders), outcome="ok")
            return Response(200, orders)
    ''',
    "app/handlers/invoices.py": '''
        from app import log, store
        from app.http import Response


        def list_invoices(conn, request):
            invoices = store.invoices_for_user(conn, request.user_id)
            log.event("invoice.list", user_id=request.user_id, count=len(invoices), outcome="ok")
            return Response(200, invoices)
    ''',
    "app/consumers/__init__.py": "",
    "app/consumers/shipping_events.py": '''
        from app import log, store


        def handle_shipment_dispatched(conn, event):
            """Called for each shipment.dispatched message. The broker delivers at least once."""
            order = store.get_order(conn, event["order_id"])
            if order is None:
                log.event("shipment.dispatched", order_id=event["order_id"], outcome="unknown_order")
                return
            if order["status"] == "shipped":
                log.event("shipment.dispatched", order_id=order["id"], outcome="duplicate")
                return
            store.set_status(conn, order["id"], "shipped")
            log.event("shipment.dispatched", order_id=order["id"], outcome="ok")
    ''',
    "app/discounts.py": '''
        def loyalty_discount_cents(total_cents, years_as_customer):
            """Customers get 2% off per full year, capped at 10%."""
            percent = min(years_as_customer * 2, 10)
            return total_cents * percent // 100
    ''',
    "tests/__init__.py": "",
    "tests/helpers.py": '''
        from app.db import connect


        def fresh_db():
            return connect()
    ''',
    "tests/test_orders.py": '''
        import unittest

        from app import store
        from app.handlers import orders
        from app.http import Forbidden, Request
        from tests.helpers import fresh_db


        class OrderHandlerTest(unittest.TestCase):
            def setUp(self):
                self.conn = fresh_db()
                self.order_id = store.create_order(self.conn, user_id=1, total_cents=500)

            def test_owner_can_read_order(self):
                resp = orders.get_order(self.conn, Request(1, {"id": self.order_id}))
                self.assertEqual(resp.body["total_cents"], 500)

            def test_other_user_is_forbidden(self):
                with self.assertRaises(Forbidden):
                    orders.get_order(self.conn, Request(2, {"id": self.order_id}))

            def test_list_returns_only_own_orders(self):
                store.create_order(self.conn, user_id=2, total_cents=900)
                resp = orders.list_orders(self.conn, Request(1))
                self.assertEqual([o["id"] for o in resp.body], [self.order_id])
    ''',
    "tests/test_invoices.py": '''
        import unittest

        from app import store
        from app.handlers import invoices
        from app.http import Request
        from tests.helpers import fresh_db


        class InvoiceHandlerTest(unittest.TestCase):
            def test_list_returns_only_own_invoices(self):
                conn = fresh_db()
                mine = store.create_invoice(conn, 1, 1, 500, "2026-01-01")
                store.create_invoice(conn, 2, 2, 900, "2026-01-02")
                resp = invoices.list_invoices(conn, Request(1))
                self.assertEqual([i["id"] for i in resp.body], [mine])
    ''',
    "tests/test_shipping_events.py": '''
        import unittest

        from app import store
        from app.consumers.shipping_events import handle_shipment_dispatched
        from tests.helpers import fresh_db


        class ShipmentDispatchedTest(unittest.TestCase):
            def test_marks_order_shipped_once_on_redelivery(self):
                conn = fresh_db()
                order_id = store.create_order(conn, 1, 500)
                handle_shipment_dispatched(conn, {"order_id": order_id})
                handle_shipment_dispatched(conn, {"order_id": order_id})
                self.assertEqual(store.get_order(conn, order_id)["status"], "shipped")
    ''',
    "tests/test_discounts.py": '''
        import unittest

        from app.discounts import loyalty_discount_cents


        class LoyaltyDiscountTest(unittest.TestCase):
            def test_cases(self):
                for total, years, expected in [(1000, 0, 0), (1000, 3, 60), (1000, 9, 100)]:
                    with self.subTest(years=years):
                        self.assertEqual(loyalty_discount_cents(total, years), expected)
    ''',
}


def orders_medium(root):
    init(root)
    first = {k: v for k, v in ORDERS.items() if "invoice" not in k and "discount" not in k}
    write(root, first)
    commit(root, "feat: orders service with ownership checks")
    write(root, {k: v for k, v in ORDERS.items() if "invoice" in k})
    commit(root, "feat: list invoices")
    write(root, {k: v for k, v in ORDERS.items() if "discount" in k})
    commit(root, "feat: loyalty discount")


# --- monorepo-large: many services sharing a common package ------------------

SERVICES = ["accounts", "billing", "catalog", "search", "notifications", "inventory",
            "shipping", "reviews", "recommendations", "analytics", "support", "media"]


def service_files(name):
    files = {f"services/{name}/__init__.py": ""}
    for i in range(1, 21):
        files[f"services/{name}/module_{i:02d}.py"] = f'''
            """{name} component {i}."""
            from common.config import setting


            def handle_{i:02d}(payload):
                limit = setting("{name}.limit_{i:02d}", 100)
                items = payload.get("items", [])[:limit]
                return {{"service": "{name}", "component": {i}, "count": len(items)}}
        '''
    files[f"tests/{name}/__init__.py"] = ""
    files[f"tests/{name}/test_{name}.py"] = f'''
        import unittest

        from services.{name}.module_01 import handle_01


        class {name.title()}Test(unittest.TestCase):
            def test_truncates_to_limit(self):
                self.assertEqual(handle_01({{"items": list(range(500))}})["count"], 100)
    '''
    return files


BILLING_EXTRA = {
    "services/billing/api.py": '''
        """Public billing API. Every handler takes (api_key, payload) and returns (status, body)."""
        from common.log import event
        from services.billing import invoices, proration


        def create_invoice(api_key, payload):
            invoice = invoices.build(payload["customer_id"], payload["lines"])
            event("billing.create_invoice", api_key=api_key, outcome="ok")
            return 201, invoice


        def change_plan(api_key, payload):
            credit = proration.credit_cents(payload["old_price_cents"], payload["days_left"], payload["days_in_period"])
            event("billing.change_plan", api_key=api_key, outcome="ok")
            return 200, {"credit_cents": credit}
    ''',
    "services/billing/invoices.py": '''
        TAX_RATE_PERCENT = 20


        def build(customer_id, lines):
            subtotal = sum(line["unit_cents"] * line["quantity"] for line in lines)
            tax = subtotal * TAX_RATE_PERCENT // 100
            return {"customer_id": customer_id, "subtotal_cents": subtotal, "tax_cents": tax,
                    "total_cents": subtotal + tax}
    ''',
    "services/billing/proration.py": '''
        def credit_cents(old_price_cents, days_left, days_in_period):
            """Credit for the unused part of the period, rounded down to the cent."""
            if days_in_period <= 0:
                raise ValueError("days_in_period must be positive")
            return old_price_cents * days_left // days_in_period
    ''',
    "tests/billing/test_invoices.py": '''
        import unittest

        from services.billing import invoices


        class InvoiceTest(unittest.TestCase):
            def test_tax_rate_is_twenty(self):
                self.assertEqual(invoices.TAX_RATE_PERCENT, 20)

            def test_build_totals(self):
                inv = invoices.build(7, [{"unit_cents": 1000, "quantity": 2}])
                self.assertEqual(inv["total_cents"], 2400)

            def test_build_totals_again(self):
                inv = invoices.build(8, [{"unit_cents": 1000, "quantity": 2}])
                self.assertEqual(inv["total_cents"], 2400)

            def test_dict_has_keys(self):
                d = {"a": 1}
                self.assertIn("a", d)

            def test_build_matches_formula(self):
                lines = [{"unit_cents": 333, "quantity": 3}]
                subtotal = sum(l["unit_cents"] * l["quantity"] for l in lines)
                self.assertEqual(invoices.build(1, lines)["tax_cents"], subtotal * 20 // 100)
    ''',
}

COMMON = {
    "common/__init__.py": "",
    "common/config.py": '''
        _SETTINGS = {}


        def setting(key, default):
            return _SETTINGS.get(key, default)
    ''',
    "common/log.py": '''
        import json
        import sys


        def event(name, **fields):
            sys.stderr.write(json.dumps({"event": name, **fields}) + "\\n")
    ''',
    "common/throttle.py": '''
        """Per-key rate limiting, shared by every service's public API."""
        import time


        class RateLimiter:
            def __init__(self, limit, per_seconds, clock=time.monotonic):
                self.limit = limit
                self.per_seconds = per_seconds
                self.clock = clock
                self._hits = {}

            def allow(self, key):
                now = self.clock()
                window = [t for t in self._hits.get(key, []) if now - t < self.per_seconds]
                if len(window) >= self.limit:
                    self._hits[key] = window
                    return False
                window.append(now)
                self._hits[key] = window
                return True
    ''',
    "services/search/api.py": '''
        from common.log import event
        from common.throttle import RateLimiter

        _limiter = RateLimiter(limit=60, per_seconds=60)


        def query(api_key, payload):
            if not _limiter.allow(api_key):
                event("search.query", api_key=api_key, outcome="rate_limited")
                return 429, {"error": "rate limited"}
            event("search.query", api_key=api_key, outcome="ok")
            return 200, {"results": []}
    ''',
    "tests/__init__.py": "",
    "tests/common/__init__.py": "",
    "tests/common/test_throttle.py": '''
        import unittest

        from common.throttle import RateLimiter


        class RateLimiterTest(unittest.TestCase):
            def test_blocks_after_limit_until_window_passes(self):
                now = [0.0]
                limiter = RateLimiter(2, 60, clock=lambda: now[0])
                self.assertTrue(limiter.allow("k"))
                self.assertTrue(limiter.allow("k"))
                self.assertFalse(limiter.allow("k"))
                now[0] = 61
                self.assertTrue(limiter.allow("k"))
    ''',
    "README.md": """
        # platform

        Monorepo for the shop platform: one package per service under `services/`,
        shared code under `common/`. Run all tests with `python3 -m unittest discover -s tests -t .`.
    """,
    "requirements.txt": "# standard library only\n",
}


def monorepo_large(root):
    init(root)
    write(root, COMMON)
    commit(root, "chore: platform skeleton and common helpers")
    for name in SERVICES:
        write(root, service_files(name))
        commit(root, f"feat({name}): add {name} service")
    write(root, BILLING_EXTRA)
    commit(root, "feat(billing): public billing API with invoices and proration")


# --- todo-web: a small todo list page over a JSON API --------------------------

TODO_WEB = {
    "README.md": """
        # todo-web

        A todo list page (`web/`) over a small JSON API (`server.py`, standard library only).
        Run it with `python3 server.py` and open http://localhost:8000. Run the tests with
        `python3 -m unittest discover -s tests -t .`.
    """,
    "server.py": '''
        import json
        from http.server import BaseHTTPRequestHandler, HTTPServer

        TODOS = {}
        NEXT_ID = [1]


        def create(title):
            todo = {"id": NEXT_ID[0], "title": title, "done": False}
            TODOS[todo["id"]] = todo
            NEXT_ID[0] += 1
            return todo


        def delete(todo_id):
            """Removes a todo; returns False when there was none with that id."""
            return TODOS.pop(todo_id, None) is not None


        class Handler(BaseHTTPRequestHandler):
            def _send(self, status, body=None):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                if body is not None:
                    self.wfile.write(json.dumps(body).encode())

            def do_GET(self):
                if self.path == "/api/todos":
                    return self._send(200, list(TODOS.values()))
                if self.path in ("/", "/index.html", "/app.js"):
                    name = "index.html" if self.path == "/" else self.path.lstrip("/")
                    self.send_response(200)
                    self.end_headers()
                    with open("web/" + name, "rb") as f:
                        self.wfile.write(f.read())
                    return
                self._send(404, {"error": "not found"})

            def do_POST(self):
                if self.path != "/api/todos":
                    return self._send(404, {"error": "not found"})
                length = int(self.headers.get("Content-Length", 0))
                title = json.loads(self.rfile.read(length) or b"{}").get("title", "").strip()
                if not title:
                    return self._send(400, {"error": "title is required"})
                self._send(201, create(title))

            def do_DELETE(self):
                prefix = "/api/todos/"
                if not self.path.startswith(prefix) or not self.path[len(prefix):].isdigit():
                    return self._send(404, {"error": "not found"})
                if not delete(int(self.path[len(prefix):])):
                    return self._send(404, {"error": "not found"})
                self._send(204)


        if __name__ == "__main__":
            HTTPServer(("localhost", 8000), Handler).serve_forever()
    ''',
    "web/index.html": """
        <!doctype html>
        <html lang="en">
        <head><meta charset="utf-8"><title>Todos</title></head>
        <body>
          <main>
            <h1>Todos</h1>
            <form id="new-todo">
              <label for="title">New todo</label>
              <input id="title" name="title" required>
              <button type="submit">Add</button>
            </form>
            <p id="status" role="status"></p>
            <ul id="todos"></ul>
          </main>
          <script src="app.js"></script>
        </body>
        </html>
    """,
    "web/app.js": '''
        const list = document.getElementById("todos");
        const status = document.getElementById("status");

        // fetch rejects when the network fails; a non-ok response is the server refusing.
        async function request(url, options) {
          try {
            return await fetch(url, options);
          } catch (error) {
            console.error("request failed", url, error);
            return {ok: false, error};
          }
        }

        async function load() {
          const res = await request("/api/todos");
          if (!res.ok) {
            status.textContent = "Could not load your todos. Try again.";
            return;
          }
          render(await res.json());
        }

        function render(todos) {
          list.replaceChildren();
          status.textContent = todos.length === 0 ? "Nothing to do yet." : "";
          for (const todo of todos) {
            const item = document.createElement("li");
            item.textContent = todo.title;
            list.append(item);
          }
        }

        document.getElementById("new-todo").addEventListener("submit", async (event) => {
          event.preventDefault();
          const input = document.getElementById("title");
          const res = await request("/api/todos", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({title: input.value}),
          });
          if (!res.ok) {
            status.textContent = "Could not add that todo. Try again.";
            return;
          }
          input.value = "";
          load();
        });

        load();
    ''',
    "tests/__init__.py": "",
    "tests/test_server.py": '''
        import unittest

        import server


        class TodoStoreTest(unittest.TestCase):
            def setUp(self):
                server.TODOS.clear()

            def test_delete_removes_an_existing_todo(self):
                todo = server.create("milk")
                self.assertTrue(server.delete(todo["id"]))
                self.assertEqual(server.TODOS, {})

            def test_delete_of_an_unknown_id_reports_none_removed(self):
                self.assertFalse(server.delete(42))


        if __name__ == "__main__":
            unittest.main()
    ''',
}


def todo_web(root):
    init(root)
    write(root, TODO_WEB)
    commit(root, "feat: todo list page over a JSON API")


# --- notifier: a mail-delivery service whose settings are stated outside the code ----

# Each delivery fact is also stated in a generated reference (docs/configuration.md), README prose, a runbook,
# .env.example, a compose file, CLI help, a docstring and the changelog, so a change that misses one shows.
NOTIFIER = {
    "notifier/__init__.py": "",
    "notifier/config.py": '''
        """Settings read from the environment once, at startup.

        SETTINGS is the single list of every setting; scripts/gen_config_docs.py renders it into
        docs/configuration.md.
        """
        import os
        from dataclasses import dataclass

        # (environment variable, default, type, description)
        SETTINGS = [
            ("NOTIFY_SMTP_HOST", "localhost", str, "SMTP server to deliver through."),
            ("NOTIFY_SMTP_PORT", "25", int, "SMTP server port."),
            ("NOTIFY_TIMEOUT_SECONDS", "10", float, "How long one delivery attempt may take before it is abandoned."),
            ("NOTIFY_DEAD_LETTER_DIR", "/var/spool/notifier/dead", str,
             "Where messages that could not be delivered are written."),
        ]


        @dataclass(frozen=True)
        class Settings:
            smtp_host: str
            smtp_port: int
            timeout_seconds: float
            dead_letter_dir: str


        def load(environ=os.environ):
            """Reads every setting from `environ`, falling back to its default."""
            values = {}
            for name, default, kind, _ in SETTINGS:
                raw = environ.get(name, default)
                try:
                    values[name] = kind(raw)
                except ValueError:
                    raise ValueError(f"{name}={raw!r} is not a valid {kind.__name__}") from None
            return Settings(
                smtp_host=values["NOTIFY_SMTP_HOST"],
                smtp_port=values["NOTIFY_SMTP_PORT"],
                timeout_seconds=values["NOTIFY_TIMEOUT_SECONDS"],
                dead_letter_dir=values["NOTIFY_DEAD_LETTER_DIR"],
            )
    ''',
    "notifier/send.py": '''
        """Delivery of one message, with retries."""
        import time

        from notifier import dead_letter

        RETRIES = 3


        class DeliveryError(Exception):
            pass


        def deliver(message, transport, settings, sleep=time.sleep):
            """Delivers `message` through `transport`.

            A failed attempt is retried up to 3 times, after 1s, 2s and 4s. When the last retry fails too, the
            message is written to the dead-letter directory and DeliveryError is raised.
            """
            last = None
            for attempt in range(RETRIES + 1):
                if attempt:
                    sleep(2 ** (attempt - 1))
                try:
                    transport.send(message, timeout=settings.timeout_seconds)
                    return attempt + 1
                except OSError as e:
                    last = e
            dead_letter.write(settings.dead_letter_dir, message)
            raise DeliveryError(f"gave up on message to {message['to']} after {RETRIES + 1} attempts: {last}")
    ''',
    "notifier/dead_letter.py": '''
        import json
        import os
        import time


        def write(directory, message):
            """Writes `message` to `directory` as one JSON file, named by time so files never collide."""
            os.makedirs(directory, exist_ok=True)
            path = os.path.join(directory, f"{time.time_ns()}.json")
            tmp = path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(message, f)
            os.replace(tmp, path)
            return path
    ''',
    "notifier/cli.py": '''
        """Command line: python3 -m notifier.cli send --to ADDRESS --subject TEXT --body TEXT"""
        import argparse
        import smtplib
        import sys

        from notifier import config, send


        class SmtpTransport:
            def __init__(self, settings):
                self.settings = settings

            def send(self, message, timeout):
                with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=timeout) as smtp:
                    smtp.sendmail("notifier@localhost", [message["to"]],
                                  f"Subject: {message['subject']}\\n\\n{message['body']}")


        def main(argv=None):
            parser = argparse.ArgumentParser(prog="notifier")
            sub = parser.add_subparsers(dest="command", required=True)
            one = sub.add_parser("send", help="send one message now; a failed attempt is retried up to 3 times")
            one.add_argument("--to", required=True)
            one.add_argument("--subject", required=True)
            one.add_argument("--body", required=True)
            args = parser.parse_args(argv)
            settings = config.load()
            message = {"to": args.to, "subject": args.subject, "body": args.body}
            try:
                attempts = send.deliver(message, SmtpTransport(settings), settings)
            except send.DeliveryError as e:
                print(e, file=sys.stderr)
                return 1
            print(f"delivered in {attempts} attempt(s)")
            return 0


        if __name__ == "__main__":
            sys.exit(main())
    ''',
    "scripts/gen_config_docs.py": '''
        """Renders notifier.config.SETTINGS as docs/configuration.md (run `make docs`)."""
        import os
        import sys

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from notifier.config import SETTINGS  # noqa: E402

        lines = [
            "<!-- Generated by scripts/gen_config_docs.py from notifier/config.py. Do not edit by hand. -->",
            "# Configuration",
            "",
            "Every setting is read from the environment at startup.",
            "",
            "| Variable | Default | Description |",
            "|---|---|---|",
        ]
        for name, default, _, description in SETTINGS:
            lines.append(f"| `{name}` | `{default}` | {description} |")
        print("\\n".join(lines))
    ''',
    "Makefile": '''
        .PHONY: test docs

        test:
        \tpython3 -m unittest discover -s tests -t .

        docs:
        \tpython3 scripts/gen_config_docs.py > docs/configuration.md
    ''',
    "tests/__init__.py": "",
    "tests/test_send.py": '''
        import tempfile
        import unittest

        from notifier import config, send


        class FlakyTransport:
            def __init__(self, failures):
                self.failures, self.calls = failures, 0

            def send(self, message, timeout):
                self.calls += 1
                if self.calls <= self.failures:
                    raise OSError("connection refused")


        def settings(directory):
            return config.load({"NOTIFY_DEAD_LETTER_DIR": directory})


        MESSAGE = {"to": "a@example.com", "subject": "hi", "body": "hello"}


        class DeliverTest(unittest.TestCase):
            def test_delivers_after_transient_failures(self):
                with tempfile.TemporaryDirectory() as d:
                    transport = FlakyTransport(failures=2)
                    self.assertEqual(send.deliver(MESSAGE, transport, settings(d), sleep=lambda s: None), 3)

            def test_gives_up_after_three_retries(self):
                with tempfile.TemporaryDirectory() as d:
                    transport, waits = FlakyTransport(failures=100), []
                    with self.assertRaises(send.DeliveryError):
                        send.deliver(MESSAGE, transport, settings(d), sleep=waits.append)
                    self.assertEqual(transport.calls, 4)
                    self.assertEqual(waits, [1, 2, 4])
    ''',
    "tests/test_config.py": '''
        import unittest

        from notifier import config


        class LoadTest(unittest.TestCase):
            def test_defaults(self):
                s = config.load({})
                self.assertEqual((s.smtp_host, s.smtp_port, s.timeout_seconds), ("localhost", 25, 10.0))

            def test_rejects_a_bad_number(self):
                with self.assertRaisesRegex(ValueError, "NOTIFY_SMTP_PORT"):
                    config.load({"NOTIFY_SMTP_PORT": "twenty-five"})
    ''',
    "README.md": '''
        # notifier

        Delivers transactional mail (receipts, password resets) through an SMTP relay.

        ## Running

        ```
        python3 -m notifier.cli send --to someone@example.com --subject "Receipt" --body "Thanks"
        ```

        Settings come from the environment; see [docs/configuration.md](docs/configuration.md) for every variable
        and its default, and `.env.example` for a starting point.

        ## Delivery

        A message that fails is retried 3 times, after 1s, 2s and 4s. If the last retry fails too, the message is
        written to the dead-letter directory, and `notifier` exits with status 1.

        ## Development

        `make test` runs the tests. `make docs` regenerates docs/configuration.md from notifier/config.py.
    ''',
    "docs/operations.md": '''
        # Operating notifier

        ## Dead letters

        Every file in `NOTIFY_DEAD_LETTER_DIR` is a message that failed 4 attempts (the first try and 3 retries,
        about 7 seconds in all). Check the SMTP relay first; once it is healthy, replay a file with:

        ```
        python3 -m notifier.cli send --to "$(jq -r .to FILE)" --subject "$(jq -r .subject FILE)" --body "$(jq -r .body FILE)"
        ```

        ## Slow relay

        A delivery attempt is abandoned after `NOTIFY_TIMEOUT_SECONDS`. With the defaults, one message can hold a
        worker for up to 47 seconds (4 attempts of 10 seconds plus 7 seconds of waiting) before it is dead-lettered.
    ''',
    ".env.example": '''
        NOTIFY_SMTP_HOST=smtp.internal
        NOTIFY_SMTP_PORT=25
        NOTIFY_TIMEOUT_SECONDS=10
        NOTIFY_DEAD_LETTER_DIR=/var/spool/notifier/dead
    ''',
    "deploy/docker-compose.yml": '''
        services:
          notifier:
            build: ..
            environment:
              NOTIFY_SMTP_HOST: smtp.internal
              NOTIFY_SMTP_PORT: "25"
              NOTIFY_TIMEOUT_SECONDS: "10"
              NOTIFY_DEAD_LETTER_DIR: /var/spool/notifier/dead
            volumes:
              - dead-letters:/var/spool/notifier/dead
        volumes:
          dead-letters: {}
    ''',
    "CHANGELOG.md": '''
        # Changelog

        ## Unreleased

        ## 1.4.0

        - Dead-lettered messages are written atomically, so a crash never leaves half a file.

        ## 1.3.0

        - `NOTIFY_TIMEOUT_SECONDS` sets how long one delivery attempt may take (default 10).
    ''',
    ".gitignore": "__pycache__/\n*.pyc\n",
    "CONTRIBUTING.md": '''
        # Contributing

        - `make test` must pass.
        - Every change a user or operator would notice gets a line under `## Unreleased` in CHANGELOG.md.
        - Commits follow Conventional Commits.
    ''',
}



def notifier(root):
    init(root)
    write(root, NOTIFIER)
    subprocess.run("python3 scripts/gen_config_docs.py > docs/configuration.md", shell=True, cwd=root, check=True)
    commit(root, "feat: notifier service")


FIXTURES = {"shop-small": shop_small, "orders-medium": orders_medium, "monorepo-large": monorepo_large,
            "todo-web": todo_web, "notifier": notifier}

if __name__ == "__main__":
    FIXTURES[sys.argv[1]](os.path.abspath(sys.argv[2]))
