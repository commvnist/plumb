---
type: llm
---
orders installs pricing-client pinned to the released version 1.4.0. Pass only if the plan says
the orders step that reads the currency waits on a pricing-client release (a new tagged or
published version) and moves the pin to it. Fail if it only orders the client change first, or
says it must be merged, without naming the release and the pin.
