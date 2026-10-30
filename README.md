# plumb marketplace

Claude Code and Codex plugin marketplace for **plumb**: one opinionated engineering philosophy across the whole development lifecycle. See [plumb/README.md](plumb/README.md).

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
- **The session-start hook,** which reminds the agent to load plumb, runs only once you trust it in `/hooks`. If you'd rather not, add its text from [plumb/hooks/session-start.md](plumb/hooks/session-start.md) to your AGENTS.md.

On Codex, agents share the session's sandbox, so the reviewer's and auditor's promise to change nothing is an instruction there, not a guarantee.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
