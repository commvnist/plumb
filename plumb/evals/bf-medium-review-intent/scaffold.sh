#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

git checkout -q -b feature/cancel-pending
python3 - <<'PY'
p = "app/handlers/orders.py"
s = open(p).read()
s += '''


def cancel_order(conn, request):
    order = store.get_order(conn, int(request.params["id"]))
    if order is None:
        raise NotFound()
    require_owner(request, order)
    store.set_status(conn, order["id"], "cancelled")
    log.event("order.cancel", user_id=request.user_id, order_id=order["id"], outcome="ok")
    return Response(200, {"order_id": order["id"], "status": "cancelled"})
'''
open(p, "w").write(s)
PY
git commit -qam "feat: let customers cancel their pending orders"
