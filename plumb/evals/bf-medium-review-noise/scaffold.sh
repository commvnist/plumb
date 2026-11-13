#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

git checkout -q -b feature/order-total
python3 - <<'PY'
p = "app/handlers/orders.py"
s = open(p).read()
s += '''


def _total_body(order):
    return {"order_id": order["id"], "total": order["total_cents"] // 100}


def get_order_total(conn, request):
    order = store.get_order(conn, int(request.params["id"]))
    if order is None:
        raise NotFound()
    require_owner(request, order)
    log.event("order.total", user_id=request.user_id, order_id=order["id"], outcome="ok")
    return Response(200, _total_body(order))
'''
open(p, "w").write(s)
PY
git commit -qam "feat: return an order's total in dollars"
