"""Builds the seeded repositories plumb's eval cases start from.

Usage: python3 make.py <fixture> <dest>
Fixtures: shop-small, orders-medium, monorepo-large.
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
            names = sorted(m.name for m in pkgutil.iter_modules(__path__) if m.name.startswith("m0"))
            for name in names:
                importlib.import_module(f"{__name__}.{name}").up(conn)
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


FIXTURES = {"shop-small": shop_small, "orders-medium": orders_medium, "monorepo-large": monorepo_large}

if __name__ == "__main__":
    FIXTURES[sys.argv[1]](os.path.abspath(sys.argv[2]))
