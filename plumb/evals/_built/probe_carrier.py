"""Calls the shipping-quote handler against a local carrier that misbehaves, and prints what came back.

Run from the repository under test: python3 probe_carrier.py ok|drip|truncated|garbage

The handler posts to an https URL. The connection class is swapped for one that reaches a plain socket on
this machine, so the real HTTP client code runs: its timeout, its parsing, its errors. A test double that
raises what its author expects can't show any of that.
"""
import http.client
import importlib
import inspect
import json
import os
import socket
import sys
import threading
import time

for name in list(os.environ):
    if name.lower().endswith("_proxy"):
        del os.environ[name]
sys.path.insert(0, os.getcwd())

SCENARIO = sys.argv[1]
BODY = b'{"price_cents": 500}'
DRIP_SECONDS = 60
hits = []
listener = socket.socket()
listener.bind(("127.0.0.1", 0))
listener.listen(8)
PORT = listener.getsockname()[1]


def head(length):
    return (b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: %d\r\n"
            b"Connection: close\r\n\r\n" % length)


def answer(conn):
    try:
        conn.settimeout(5)
        seen = b""
        while b"\r\n\r\n" not in seen:
            chunk = conn.recv(65536)
            if not chunk:
                break
            seen += chunk
        if SCENARIO == "ok":
            conn.sendall(head(len(BODY)) + BODY)
        elif SCENARIO == "drip":
            # One byte a second: every read succeeds, so only a bound on the whole call ends it.
            padded = BODY + b" " * (DRIP_SECONDS - len(BODY))
            conn.sendall(head(len(padded)))
            for byte in padded:
                conn.sendall(bytes([byte]))
                time.sleep(1)
        elif SCENARIO == "truncated":
            conn.sendall(head(200) + BODY)
        elif SCENARIO == "garbage":
            conn.sendall(b"NOT HTTP AT ALL\r\n\r\n")
    except OSError:
        pass
    finally:
        conn.close()


def serve():
    while True:
        conn, _ = listener.accept()
        hits.append(1)
        threading.Thread(target=answer, args=(conn,), daemon=True).start()


class Local(http.client.HTTPConnection):
    def __init__(self, host, port=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, **ignored):
        super().__init__("127.0.0.1", PORT, timeout=timeout)


http.client.HTTPSConnection = Local
threading.Thread(target=serve, daemon=True).start()

from app import store  # noqa: E402
from app.db import connect  # noqa: E402
from app.http import Request, Response  # noqa: E402

module = importlib.import_module("app.handlers.shipping")
handlers = [f for n, f in vars(module).items()
            if inspect.isfunction(f) and f.__module__ == module.__name__ and not n.startswith("_")
            and len(inspect.signature(f).parameters) == 2]
handlers.sort(key=lambda f: "quote" not in f.__name__)
conn = connect()
order_id = store.create_order(conn, 7, 2500)
conn.commit()
started = time.monotonic()
try:
    result = handlers[0](conn, Request(7, params={"id": order_id, "order_id": order_id}))
    outcome = f"response:{result.status}" if isinstance(result, Response) else f"returned:{type(result).__name__}"
except Exception as e:  # the grader's subject is exactly which exception escapes
    cls = type(e)
    outcome = f"raised:{cls.__module__}.{cls.__name__}"
print(json.dumps({"outcome": outcome, "elapsed": round(time.monotonic() - started, 1), "hits": len(hits)}))
