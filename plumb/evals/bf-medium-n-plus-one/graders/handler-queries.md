---
type: llm
focus: {source: file, path: app/handlers/orders.py}
---
This is app/handlers/orders.py after the change. Pass if the new handler does not run one query
per order (such as calling invoices_for_order inside a loop over the orders); it gets the invoices
for all the orders with a fixed number of store calls, however many orders there are.
