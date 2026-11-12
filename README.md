# plumb marketplace

Claude Code, Codex and GitHub Copilot CLI plugin marketplace for **plumb**: one opinionated engineering philosophy across the whole development lifecycle. See [plumb/README.md](plumb/README.md).

## Install

```
/plugin marketplace add commvnist/plumb
/plugin install plumb@plumb-marketplace
```

Update later with `/plugin marketplace update plumb-marketplace`.

### Codex

Untested: Codex support is built from OpenAI's documentation and hasn't been run yet. Reports of what works and what doesn't are welcome.

```
codex plugin marketplace add commvnist/plumb
codex plugin add plumb
```

Codex reads the same skills. Two parts need a step from you:

- **Agents.** Codex plugins can't ship agents, so copy plumb's from a clone of this repository: `cp plumb/codex/agents/*.toml ~/.codex/agents/` (or a project's `.codex/agents/`). To pick a model for one, add a `model = "<name>"` line to its copy. Without the copies, use `- plumb agents: off` in your AGENTS.md (see [Choosing models](plumb/README.md#choosing-models)).
- **The hooks,** one that reminds the agent to load plumb and one that asks it to fix a commit message that isn't Conventional Commits, run only once you trust them in `/hooks`. If you'd rather not, add the reminder's text from [plumb/hooks/session-start.md](plumb/hooks/session-start.md) to your AGENTS.md. The commit check is untested on Codex.

On Codex, agents share the session's sandbox, so the reviewer's and auditor's promise to change nothing is an instruction there, not a guarantee.

### GitHub Copilot CLI

```
copilot plugin marketplace add commvnist/plumb
copilot plugin install plumb@plumb-marketplace
```

Copilot CLI reads this plugin as it is: the skills, the agents (with the same tool limits as in Claude Code) and both hooks. It was run with Copilot CLI 1.0.109 against a stand-in model, which showed each part loading, the hooks' text reaching the model and an agent starting on the model it was given; it hasn't yet been used for real work with Copilot's own models. A `plumb agents:` line goes in your AGENTS.md or `.github/copilot-instructions.md` (see [Choosing models](plumb/README.md#choosing-models)).

Copilot's cloud agent, which works on issues in GitHub, doesn't load plugins, and VS Code's plugin support hasn't been tried.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
