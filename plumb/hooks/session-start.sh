#!/bin/sh
# Gives the agent plumb's reminder when a session starts. Claude Code and Codex take
# plain output as context; Copilot CLI takes only JSON with a top-level additionalContext.
reminder="$(dirname "$0")/session-start.md"
if [ -n "$COPILOT_PLUGIN_ROOT" ]; then
  text=$(sed 's/\\/\\\\/g; s/"/\\"/g' "$reminder" | awk '{ printf "%s%s", (NR > 1 ? "\\n" : ""), $0 }')
  printf '{"additionalContext":"%s"}\n' "$text"
else
  cat "$reminder"
fi
