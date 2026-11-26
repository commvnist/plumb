#!/bin/sh
# Runs after each shell command. Charter rule 20's offer to record what was costly to learn is easy to
# lose in a long session, where the work that taught it is far behind; a push or a new pull request is
# where the work leaves the session, so the first one in a session (or since its last compaction) carries
# a one-line reminder. Said once: where the transcript already holds it, or can't be read, nothing is said.
input=$(cat)

command=$(printf '%s' "$input" | grep -Eo '"command" *: *"([^"\\]|\\.)*"' | head -n 1)
# A newline inside the JSON command is the two characters \n, so it counts as a boundary too.
printf '%s' "$command" | grep -Eq '(^|[^[:alnum:]_-]|\\n)(git([[:space:]][^;&|]*)?[[:space:]]push|gh[[:space:]]+pr[[:space:]]+create)([[:space:]]|\\|"|$)' || exit 0
# Work that didn't leave has nothing to wrap up yet. A push that went through can still print "fatal:"
# (a failed negotiation it recovers from), so only a sign that it went through counts: a ref update, a
# branch already up to date, or the new pull request's address. A tool that reports no output passes.
if printf '%s' "$input" | grep -Eq '"tool_response" *:'; then
  printf '%s' "$input" | sed -n 's/.*"tool_response" *: *//p' \
    | grep -Eq ' -> |Everything up-to-date|/pull/[0-9]' || exit 0
  printf '%s' "$input" | sed -n 's/.*"tool_response" *: *//p' | grep -Eq '\[rejected\]|failed to push' && exit 0
fi

reminder="plumb: work just left this session. Before wrapping up, charter rule 20: offer to record anything this session found costly to learn and likely to recur."

transcript=$(printf '%s' "$input" | grep -Eo '"transcript_path" *: *"([^"\\]|\\.)*"' | head -n 1 \
  | sed 's/.*: *"//; s/"$//; s/\\\\/\\/g')
agent=$(printf '%s' "$input" | grep -Eo '"agent_id" *: *"[A-Za-z0-9_-]+"' | head -n 1 | sed 's/.*: *"//; s/"$//')
[ -n "$agent" ] && transcript="${transcript%.jsonl}/subagents/agent-$agent.jsonl"
[ -r "$transcript" ] || exit 0
# Only what follows the last compaction is in the agent's context.
said=$(awk -v r="$reminder" '
  index($0, "\"subtype\":\"compact_boundary\"") { said = 0; next }
  index($0, r) { said = 1 }
  END { print said + 0 }' "$transcript")
[ "$said" = 0 ] || exit 0

if [ -n "$COPILOT_PLUGIN_ROOT" ]; then
  printf '{"additionalContext":"%s"}\n' "$reminder"
else
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$reminder"
fi
