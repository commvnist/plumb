#!/bin/sh
# Gives the agent plumb's reminder when a session starts, with the installed version so two
# versions in one session show. After a compaction, the skills loaded before it are gone from
# context, so it also says to load them again. Claude Code and Codex take plain output as
# context; Copilot CLI takes only JSON with a top-level additionalContext.
here=$(dirname "$0")
input=""
[ -t 0 ] || input=$(cat)
version=$(grep -Eho '"version" *: *"[^"]*"' "$here/../.claude-plugin/plugin.json" "$here/../.codex-plugin/plugin.json" 2>/dev/null \
  | head -n 1 | sed 's/.*: *"//; s/"$//')
reminder=$(sed "1s/^The plumb plugin is installed\./The plumb plugin${version:+ $version} is installed./" "$here/session-start.md")
if printf '%s' "$input" | grep -Eq '"source" *: *"compact"'; then
  reminder="$reminder
The conversation was just compacted, so plumb skills loaded before it are no longer in context: load the charter and the skill for the current phase again before the next change."
fi
if [ -n "$COPILOT_PLUGIN_ROOT" ]; then
  text=$(printf '%s\n' "$reminder" | sed 's/\\/\\\\/g; s/"/\\"/g' | awk '{ printf "%s%s", (NR > 1 ? "\\n" : ""), $0 }')
  printf '{"additionalContext":"%s"}\n' "$text"
else
  printf '%s\n' "$reminder"
fi
