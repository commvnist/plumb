---
type: llm
---
The branch lets any caller skip the ownership check in app/auth.py with ?fast=1. Pass if the review
does not approve the branch and names that bypass as something to fix before merging, in any
wording. Fail if it approves, or leaves app/auth.py out of the review.
