#!/bin/sh
# Runs before each edit and shell command; of the shell commands, only a commit or push counts.
# A reminder can fade behind later context, so the first such call in a session (or since
# its last compaction) whose context holds no sign of the charter is refused with a note to load it.
# Refused once only: the agent then decides, and a repeat goes through, so work
# that isn't code is never trapped. Without a readable transcript (Copilot CLI
# gives none here) the call goes through, since a hook error would refuse it.
input=$(cat)

# A newline inside the JSON command is the two characters \n, so it counts as a boundary too.
case $(printf '%s' "$input" | grep -o '"tool_name" *: *"[^"]*"' | head -n 1) in
  *'"Bash"') printf '%s' "$input" | grep -Eo '"command" *: *"([^"\\]|\\.)*"' | head -n 1 \
      | grep -Eq '(^|[^[:alnum:]_-]|\\n)git([[:space:]][^;&|]*)?[[:space:]](commit|push)([[:space:]]|\\|"|$)' || exit 0 ;;
  *'"Edit"' | *'"Write"' | *'"NotebookEdit"' | *'"apply_patch"') ;;
  *) exit 0 ;;
esac

# A Windows path arrives JSON-escaped (C:\\Users\\...), so undo the escaping before reading it.
transcript=$(printf '%s' "$input" | grep -Eo '"transcript_path" *: *"([^"\\]|\\.)*"' | head -n 1 \
  | sed 's/.*: *"//; s/"$//; s/\\\\/\\/g')
# A subagent's calls arrive with the session's transcript and the agent's id; its own context, refusals
# included, is in the agent's transcript beside it.
agent=$(printf '%s' "$input" | grep -Eo '"agent_id" *: *"[A-Za-z0-9_-]+"' | head -n 1 | sed 's/.*: *"//; s/"$//')
[ -n "$agent" ] && transcript="${transcript%.jsonl}/subagents/agent-$agent.jsonl"
[ -r "$transcript" ] || exit 0

# A compaction replaces everything before it with a summary, so only what follows the last one is in the
# agent's context; the summary itself is left out, since it may name the charter without holding it.
# One pass: 1 when the charter is in that context, 2 when this hold was already given there.
reason="plumb held this call: the plumb charter isn't loaded in this session."
charter="$(dirname "$0")/../skills/plumb/SKILL.md"
marker=$(awk 'found && NF { print; exit } /^# Plumb$/ { found = 1 }' "$charter")
[ -n "$marker" ] || exit 0
seen=$(awk -v m="$marker" -v r="$reason" '
  index($0, "\"subtype\":\"compact_boundary\"") { charter = 0; held = 0; next }
  index($0, "\"isCompactSummary\":true") { next }
  index($0, m) { charter = 1 }
  index($0, r) { held = 1 }
  END { print (charter ? 1 : held ? 2 : 0) }' "$transcript")
[ "$seen" = 0 ] || exit 0

reason="$reason Load the plumb skill (the charter) and the plumb skill for this phase, then make the call again. If the work isn't code, make the call again as it is; it won't be held twice."
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
