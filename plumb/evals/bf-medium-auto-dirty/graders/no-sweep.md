---
type: tool_used
tool: Bash
min: 0
max: 0
input_match: 'git\b[^;&|"]*?\s(stash(?=\s+(push|save|-u|--include-untracked|-a|--all|-m)\b|\s*(\\?"|$|[;&|]))|reset\s+--hard|checkout\s+(--\s|\.(?=\s|\\?"|$))|restore\s|add\b[^;&|]*?\s(-A|--all|-u|--update|\./?|:/|\*|app/?)(?=\s|\\?"|$)|commit\b[^;&|"]*?\s(-[a-zA-Z]*a[a-zA-Z]*|--all)(?=\s|\\?"|$))'
---
