---
type: llm
focus: {source: file, path: web/app.js}
---
This is web/app.js after the change. Pass if each todo's delete control is a real button (a
<button> element, or an element with a button role that also works from the keyboard) whose
accessible name says what it does (visible text such as "Delete", or an aria-label naming the
todo). Fail if it is a clickable span, div or icon with no accessible name.
