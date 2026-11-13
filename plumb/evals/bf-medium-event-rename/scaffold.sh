#!/bin/bash
set -euo pipefail
. "$(dirname "$0")/../_fixtures/seed.sh" orders-medium

cat > app/shipping.py <<'PY'
from app import log


def dispatch(broker, order_id):
    # Publishes shipment.dispatched once the parcel leaves the warehouse.
    broker.publish("shipment.dispatched", {"order_id": order_id})
    log.event("shipment.publish", order_id=order_id, outcome="ok")
PY
git add -A && git commit -qm "Publish shipment.dispatched from the warehouse flow"
