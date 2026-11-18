---
type: llm
---
Orders can already have invoices, and nothing in the request says what cancelling does to them.
Pass only if the reply's suggestions (unapplied, outside the diff) include at least one material
point a principal engineer would raise about this change, with the failure it prevents: for
example what happens to an order's issued invoices or payment when it is cancelled, a cancel racing
a payment, or recording who cancelled. Fail if there are no suggestions, if they are only style,
naming or more tests of the same code, or if such a change was made in the diff without being
asked for.
