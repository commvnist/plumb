---
type: llm
---
Below is the reply; judge what it says the handler does when the carrier is down, slow, or
answers with an error or malformed body. Pass if those failures reach the handler's caller as a
defined response or as an error type of the project's own (such as a 502, or a new exception
beside the project's NotFound and Forbidden), never as a raw urllib, socket or JSON exception.
Fail if the reply doesn't say how carrier failures are handled.
