"""Sends badly framed requests to the todo server's retitle route and prints how each was answered.

Run from the repository under test: python3 probe_framing.py

Each request is written to a raw socket, since an HTTP client library would refuse to send it. A request
passes when the server answers it with a 4xx within the time limit and still serves the next one.
"""
import json
import os
import socket
import subprocess
import sys
import time

LIMIT = 3
START = ("import server; from http.server import HTTPServer; s = HTTPServer(('127.0.0.1', 0), server.Handler);"
         " print(s.server_address[1], flush=True); s.serve_forever()")


def exchange(port, raw):
    """The status code the server answers with, or None when it hangs or drops the connection."""
    with socket.create_connection(("127.0.0.1", port), timeout=LIMIT) as s:
        s.sendall(raw)
        try:
            first = s.recv(4096)
        except OSError:
            return None
    parts = first.split(b" ", 2)
    return int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None


def request(method, path, body=b"", length=None):
    length = str(len(body)).encode() if length is None else length
    return (method + b" " + path + b" HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\n"
            b"Content-Length: " + length + b"\r\nConnection: close\r\n\r\n" + body)


server = subprocess.Popen([sys.executable, "-c", START], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          cwd=os.getcwd(), text=True)
try:
    port = int(server.stdout.readline())
    exchange(port, request(b"POST", b"/api/todos", b'{"title": "milk"}'))
    listed = socket.create_connection(("127.0.0.1", port), timeout=LIMIT)
    listed.sendall(request(b"GET", b"/api/todos"))
    todo_id = str(json.loads(listed.makefile("rb").read().split(b"\r\n\r\n", 1)[1])[0]["id"]).encode()
    listed.close()
    path = b"/api/todos/" + todo_id
    good = b'{"title": "oat milk"}'
    method = next((m for m in (b"PATCH", b"PUT") if (exchange(port, request(m, path, good)) or 500) < 300), None)
    report = {"method": method.decode() if method else None, "requests": {}}
    if method:
        probes = {
            "negative-length": request(method, path, good, length=b"-1"),
            "non-numeric-length": request(method, path, good, length=b"abc"),
            "non-ascii-digit-id": request(method, b"/api/todos/\xb2", good),
            "body-not-an-object": request(method, path, b"[]"),
        }
        for name, raw in probes.items():
            status = exchange(port, raw)
            time.sleep(0.2)
            alive = exchange(port, request(b"GET", b"/api/todos")) == 200
            report["requests"][name] = {"status": status, "served_next": alive}
    print(json.dumps(report))
finally:
    server.kill()
