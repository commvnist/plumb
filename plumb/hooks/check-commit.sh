#!/bin/sh
# Runs after each shell command. Skill text alone can't guarantee a commit's
# format, so this catches a commit just made whose subject isn't Conventional
# Commits, or that credits an AI tool, and asks the agent to fix it while it's still unpushed and cheap.
input=$(cat)

# Only the command counts: a command's output can mention commits too.
command=$(printf '%s' "$input" | grep -Eo '"command" *: *"([^"\\]|\\.)*"' | head -n 1)
printf '%s' "$command" | grep -Eq '(^|[^[:alnum:]_-])git([[:space:]][^;&|]*)?[[:space:]]commit([[:space:]]|\\|"|$)' || exit 0

dir=$(printf '%s' "$input" | grep -o '"cwd" *: *"[^"]*"' | head -n 1 | sed 's/.*: *"//; s/"$//')
[ -n "$dir" ] || dir=.
git -C "$dir" rev-parse --git-dir >/dev/null 2>&1 || exit 0

# Only a commit this command made: the newest reflog entry is a commit, and recent.
entry=$(git -C "$dir" reflog -1 --date=unix --format='%gd %gs' 2>/dev/null) || exit 0
case $entry in
  *"} commit (merge):"*) exit 0 ;;
  *"} commit"*) ;;
  *) exit 0 ;;
esac
made=$(printf '%s' "$entry" | sed 's/^[^{]*{\([0-9]*\)}.*/\1/')
[ $(( $(date +%s) - made )) -le 120 ] || exit 0

subject=$(git -C "$dir" log -1 --format=%s)
body=$(git -C "$dir" log -1 --format=%b)
note=""
if ! printf '%s\n' "$subject" | grep -Eq '^(feat|fix|perf|refactor|test|docs|build|ci|chore|style|revert)(\([^()]+\))?!?: [^ ]'; then
  note=" Its subject isn't Conventional Commits."
fi
# A trailer or line crediting an AI tool, which plumb's charter rule 20 rules out.
if printf '%s\n' "$body" | grep -Eiq '^(co-authored-by|generated-by|assisted-by|[a-z]+-session):.*(claude|anthropic|openai|codex|copilot|gemini|cursor|\bai\b)|generated (with|by) .*(claude|codex|copilot|gemini|cursor|\bai\b)'; then
  note="$note It credits an AI tool (a co-author, generated-by or session line); rule 20 says to remove it."
fi
[ -n "$note" ] || exit 0

note="plumb: check the commit just made.$note Unless the user asked for this exact message or the project's written rules set another format, load plumb-ship and amend the message to its format, keeping the rest of the body. If the commit is already pushed, don't rewrite it: tell the user and propose the corrected message."
# Copilot CLI reads context only from a top-level field; Claude Code from hookSpecificOutput.
if [ -n "$COPILOT_PLUGIN_ROOT" ]; then
  printf '{"additionalContext":"%s"}\n' "$note"
else
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$note"
fi
