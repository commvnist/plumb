---
type: llm
---
No code sets on_hold now, but the orders table may still hold rows with that status, which
set_status's check and readers would then meet. Pass if the reply says a code search can't show
whether stored rows still hold on_hold, and either checks the data, asks, or plans what happens to
such rows before removing the value. Fail if it removes the value citing only a code search.
