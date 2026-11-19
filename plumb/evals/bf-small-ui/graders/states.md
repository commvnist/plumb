---
type: llm
focus: {source: file, path: web/app.js}
---
This is web/app.js after the change. Pass only if both hold:
- When the delete request fails (a non-ok response or a network error), the todo is not silently
  dropped: it stays or comes back, and the status area tells the user it wasn't deleted.
- Deleting the last todo leaves the empty-list message showing.
