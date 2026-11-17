#!/bin/sh
# Runs before each edit and shell command; of the shell commands, only a commit or push counts.
# A reminder can fade behind later context, so the first such call in a session
# whose transcript holds no sign of the charter is refused with a note to load it.
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

transcript=$(printf '%s' "$input" | grep -o '"transcript_path" *: *"[^"]*"' | head -n 1 | sed 's/.*: *"//; s/"$//')
[ -r "$transcript" ] || exit 0

# The charter's opening line marks it as loaded, however it arrived. It holds no
# quote or backslash, so it reads the same inside the transcript's JSON.
charter="$(dirname "$0")/../skills/plumb/SKILL.md"
marker=$(awk 'found && NF { print; exit } /^# Plumb$/ { found = 1 }' "$charter")
reason="plumb held this call: the plumb charter isn't loaded in this session."
[ -n "$marker" ] || exit 0
grep -qF "$marker" "$transcript" && exit 0
grep -qF "$reason" "$transcript" && exit 0

reason="$reason Load the plumb skill (the charter) and the plumb skill for this phase, then make the call again. If the work isn't code, make the call again as it is; it won't be held twice."
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
