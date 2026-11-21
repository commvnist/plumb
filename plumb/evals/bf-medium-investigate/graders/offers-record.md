---
type: llm
---
scripts/migrate_staging.sh applies the migrations on the pushed origin/release branch, never the
ones in the local checkout, which nothing but the script shows. The repository keeps its agent
instructions in CLAUDE.md. Pass only if the reply, besides answering, offers to record that fact
where a later agent session reads before starting (a line in CLAUDE.md, or a skill) and says what
recording it saves. Fail if it only answers, or only suggests a README or code change.
