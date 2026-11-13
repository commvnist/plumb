#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat > app/payments.py <<'PY'
class PaymentDeclined(Exception):
    pass


def charge(card, amount_cents):
    # Charges the card through the payment gateway and returns its transaction id.
    # card is {"number", "cvc", "exp_month", "exp_year", "holder_name"}. Raises PaymentDeclined.
    raise NotImplementedError("gateway client is configured in production")
PY
cat > app/handlers/payments.py <<'PY'
from app import payments, store
from app.auth import require_owner
from app.http import NotFound, Response


def pay_order(conn, request):
    order = store.get_order(conn, int(request.params["id"]))
    if order is None:
        raise NotFound()
    require_owner(request, order)
    try:
        payments.charge(request.body["card"], order["total_cents"])
    except payments.PaymentDeclined:
        return Response(402, {"error": "payment declined"})
    store.set_status(conn, order["id"], "paid")
    return Response(200, {"status": "paid"})
PY
git add -A && git commit -qm "feat: pay for an order"
