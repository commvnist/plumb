# plumb marketplace

Claude Code, Codex and GitHub Copilot CLI plugin marketplace for **plumb**: one opinionated engineering philosophy across the whole development lifecycle. See [plumb/README.md](plumb/README.md).

## Install

```
/plugin marketplace add commvnist/plumb
/plugin install plumb@plumb-marketplace
```

To update, refresh the marketplace inside Claude Code:

```
/plugin marketplace update plumb-marketplace
```

then update the plugin from a terminal and restart Claude Code:

```
claude plugin update plumb@plumb-marketplace
```

The first command only refreshes the list of versions; the second installs the new one. To have both happen on their own, choose plumb-marketplace under Marketplaces in `/plugin` and enable auto-update. `claude plugin list` shows the version you're running. Install plumb from one place only: if it also reaches you through your claude.ai account, the two copies can differ in version and both run.

### How plumb gets loaded

No plugin can make the agent load a skill, so three hooks keep the charter from being skipped. At session start the agent is told to load plumb for code work; each new request gets a one-line reminder; and the first edit, commit or push in a session, or since its last compaction, where the charter isn't in the agent's context is held once with a note to load it. The session-start reminder names the installed version, so a session that mixes two versions shows it. A repeat of the held call goes through, so work that isn't code is never stopped. Shell commands are matched by pattern, so an edit made by a script isn't held. The hold works in Claude Code; on Copilot CLI it does nothing (see below), and on Codex it is untested.

### What plumb can and can't stop

Plumb's rules are instructions to the agent, not locks. "Nothing outside the diff changes without a yes" (a shared database, a production system, your uncommitted work) is something the agent follows, not something the plugin enforces, and the "read-only" agents still have a shell. To make a live system unreachable, deny it in your tool's permission settings (in Claude Code, `permissions.deny` in settings.json), and keep production credentials out of the agent's environment.

The commit check reads commits in repositories on the agent's machine and text posted with `gh`. A commit the agent hands to another machine, container or job runner is checked only by the text of the command that sends it, and text posted through other tools (an issue tracker's CLI, a chat) isn't checked at all; there, the voice and Conventional Commits rules rest on the agent alone.

To keep your tool from adding its own co-author line or "Generated with" footer, which plumb otherwise has to ask the agent to remove after each commit, turn it off at the source: in Claude Code, set `"attribution": {"commit": "", "pr": ""}` in settings.json.

### Codex

Untested: Codex support is built from OpenAI's documentation and hasn't been run yet. Reports of what works and what doesn't are welcome.

```
codex plugin marketplace add commvnist/plumb
codex plugin add plumb
```

Codex reads the same skills. Two parts need a step from you:

- **Agents.** Codex plugins can't ship agents, so copy plumb's from a clone of this repository: `cp plumb/codex/agents/*.toml ~/.codex/agents/` (or a project's `.codex/agents/`), and copy them again after each update, since the copies don't update with the plugin. To pick a model for one, add a `model = "<name>"` line to its copy. Without the copies, use `- plumb agents: off` in your AGENTS.md (see [Choosing models](plumb/README.md#choosing-models)).
- **The hooks** (the ones that get plumb loaded, and one that asks the agent to fix a commit message that isn't Conventional Commits or that credits an AI tool) run only once you trust them in `/hooks`. If you'd rather not, add the reminder's text from [plumb/hooks/session-start.md](plumb/hooks/session-start.md) to your AGENTS.md. All but the session reminder are untested on Codex, including whether a held call goes through when repeated.

On Codex, agents share the session's sandbox, so the reviewer's and auditor's promise to change nothing is an instruction there, not a guarantee.

### GitHub Copilot CLI

```
copilot plugin marketplace add commvnist/plumb
copilot plugin install plumb@plumb-marketplace
```

Copilot CLI reads this plugin as it is: the skills, the agents (with the same tool limits as in Claude Code), the session reminder and the commit check. By Copilot's documentation it drops a per-request hook's text and gives the edit hook no transcript, so the per-request reminder and the held first edit, commit or push do nothing there. It was run with Copilot CLI 1.0.109 against a stand-in model, which showed each part loading, the hooks' text reaching the model and an agent starting on the model it was given; it hasn't yet been used for real work with Copilot's own models. A `plumb agents:` line goes in your AGENTS.md or `.github/copilot-instructions.md` (see [Choosing models](plumb/README.md#choosing-models)).

Copilot's cloud agent, which works on issues in GitHub, doesn't load plugins, and VS Code's plugin support hasn't been tried.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
