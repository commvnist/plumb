---
type: llm
focus: {source: file, path: services/billing/api.py}
---
Pass if the billing API reuses common.throttle.RateLimiter rather than a new limiter, applies it
to every public billing handler, and on the limit returns 429 and logs a rate_limited outcome.
