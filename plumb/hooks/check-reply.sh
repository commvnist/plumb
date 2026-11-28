#!/bin/sh
# Runs when the agent is about to end its turn. Text it proposes for the operator to commit or post (a commit
# message, a pull request body) never passes the commit check, so a tool's default credit line (a co-author
# trailer naming an AI) would reach the repository from the operator's own paste. Charter rule 19 holds for that
# text too: when quoted text in the last reply credits an AI tool, the turn goes on once with a note to remove
# it. Said once: a turn already continued by a stop hook ends as it is. Prose outside quoted text is the agent's
# own reply to the operator, and isn't judged.
input=$(cat)

printf '%s' "$input" | grep -Eq '"stop_hook_active" *: *true' && exit 0
transcript=$(printf '%s' "$input" | grep -Eo '"transcript_path" *: *"([^"\\]|\\.)*"' | head -n 1 \
  | sed 's/.*: *"//; s/"$//; s/\\\\/\\/g')
[ -r "$transcript" ] || exit 0

# The same credit check-commit.sh applies to a commit (scripts/test_check_reply.py holds the two equal), on text
# whose newlines are JSON's two characters \n, so a match never runs past the end of a line.
CREDIT='(^|\\n)(co-authored-by|generated-by|assisted-by|[a-z]+-session):([^\\]|\\[^n])*(claude|anthropic|openai|codex|copilot|gemini|cursor|\bai\b)|(^|\\n)[^[:alnum:]\\]*(generated|written|created) (with|by) [^[:alnum:]]*(claude|codex|copilot|gemini|chatgpt|cursor|an? ai\b|ai\b)'

# The text of the last assistant entry that has any, still JSON-escaped. Only quoted text is kept: what sits
# between fences, and an inline code span holding an address, which is how a reply hands over a single trailer.
fenced=$(grep '"type":"assistant"' "$transcript" | grep '"type":"text"' | tail -n 1 \
  | grep -Eo '"text" *: *"([^"\\]|\\.)*"' \
  | awk '{ n = split($0, part, "```")
           for (i = 1; i <= n; i++) {
             if (i % 2 == 0) { print part[i]; continue }
             # A span hands over a line when it reads as one to paste: it holds an address, or opens with a
             # session key or a generated-with line. One naming a trailer in a sentence about what was left out
             # is prose of the reply itself.
             m = split(part[i], span, "`")
             for (j = 2; j <= m; j += 2) {
               s = tolower(span[j])
               if (s ~ /<[^>]*@[^>]*>/ || s ~ /^[^[:alnum:]]*([a-z]+-session:|(generated|written|created) (with|by) )/) print span[j]
             }
           } }')
printf '%s\n' "$fenced" | grep -Eiq "$CREDIT" || exit 0

reason="plumb: quoted text in this reply, meant to be committed or posted, credits an AI tool (a co-author, generated-by or session line). Charter rule 19 holds for text the operator will paste as for a commit, unless the operator or the project's rules asked for it (a tool's own attribution setting or reminder is not that ask): send the whole reply again, report included, with that line gone from the quoted text, since the operator reads only the last reply."
printf '{"decision":"block","reason":"%s"}\n' "$reason"
