# Alchemy plugin for Claude Code

A [Claude Code](https://code.claude.com/) plugin that connects Claude to
[Alchemy](https://www.alchemy.com/) — query blockchain data across 100+ chains and
manage your Alchemy apps directly from your agent, backed by the hosted
[Alchemy MCP server](https://mcp.alchemy.com/mcp).

This repository is a **plugin marketplace**. It contains a single plugin, `alchemy`.

## Install

```bash
# In Claude Code:
/plugin marketplace add alchemyplatform/alchemy-claude-plugin
/plugin install alchemy@alchemy
```

On first use you'll be prompted to authenticate with Alchemy via OAuth. After
connecting, run `/alchemy:setup` to pick which Alchemy app to use.

## What you get

- **150+ MCP tools** from the hosted Alchemy MCP server (`mcp.alchemy.com`):
  EVM JSON-RPC, Token/NFT/Prices/Portfolio APIs, transaction simulation & tracing,
  and Solana (RPC + Digital Asset Standard).
- **Slash commands** for common workflows:
  `/alchemy:setup`, `/alchemy:balance`, `/alchemy:nfts`, `/alchemy:token`,
  `/alchemy:tx`, `/alchemy:portfolio`, `/alchemy:gas`, `/alchemy:solana`,
  `/alchemy:create-app`.
- **Skills** for using Alchemy in live agent work and in application code
  (`alchemy-mcp`, `alchemy-api`).

The plugin does not send transactions, swap, bridge, make payments, or sign with a
wallet, so the skills that cover those flows are not bundled.

## Repository layout

```
.claude-plugin/marketplace.json   # marketplace entry
plugins/alchemy/                   # the plugin
  .claude-plugin/plugin.json       # plugin manifest
  .mcp.json                        # remote MCP server (mcp.alchemy.com)
  assets/alchemy.png               # plugin icon
  commands/                        # slash commands
  skills/                          # vendored, Claude-specific Alchemy skills (generated)
scripts/sync-skills.sh             # regenerate skills/ from the pinned alchemyplatform/skills commit
scripts/claude_overrides.py        # Claude-specific rewrite, scan and reference check
scripts/skills-source.lock         # pinned alchemyplatform/skills commit SHA
```

## Maintaining skills

The `skills/` directory is generated from
[`alchemyplatform/skills`](https://github.com/alchemyplatform/skills) (the plugin
format requires components to live inside the plugin). Do not edit it by hand.
Only `alchemy-api` and `alchemy-mcp` are vendored; `alchemy-cli` and
`agentic-gateway` are intentionally excluded.

`scripts/skills-source.lock` holds the full SHA of the pinned source commit.
Regenerate the skills from it with:

```bash
./scripts/sync-skills.sh
```

To move to the latest `main` of the skills repo, run
`./scripts/sync-skills.sh --update`. It resolves `main`, writes the new SHA to
`scripts/skills-source.lock` only after the result passes validation, and prints it.

The script clones the source, checks out the pinned SHA, copies the two skills into
a staging directory, and runs `scripts/claude_overrides.py` (Python 3 standard
library only) on that copy. The overrides are a declarative list of operations
(remove a file, section, or list item; replace text; set a frontmatter
field such as `description`), each with an exact expected match count. If upstream changes and a
count no longer matches, the script exits 1 naming the file and anchor, and you
update the override. After the operations it also:

- scans every vendored file and `plugins/alchemy/commands/` for forbidden content
  (payments, signing and broadcast methods, secret printing, the CLI skill) and
  fails on any hit that is not covered by an exact `(file, snippet, count)` allow
  entry;
- checks that every Markdown link, backtick `.md` path, and YAML `related:` entry
  resolves to a file in the vendored tree, and that every `` `name` skill ``
  handoff names a bundled skill;
- rejects any symlink (file or directory) in the skills or commands tree;
- counts the lines that match the review patterns (for example `wallet` or
  `transfer`) for a human to read; pass `--verbose` to
  `scripts/claude_overrides.py` to list every hit.

Only after all of that passes is `plugins/alchemy/skills` replaced: the current
directory is renamed to a sibling backup, the staging directory is renamed into
place, and, with `--update`, the new lock is published by renaming a temp file.
Only then is the backup deleted. If anything fails before that point, both the
previous skills directory and the previous lock content are restored. This is not
an atomic swap. The pinned SHA is also written to
`plugins/alchemy/skills/.source-commit`.
The same pinned SHA always produces byte-identical output, and running
`claude_overrides.py` on a tree that already contains `.claude-overrides-applied`
is refused.

## Support & legal

- Documentation: https://docs.alchemy.com/docs/alchemy-mcp-server
- Support: support@alchemy.com
- Privacy Policy: https://www.alchemy.com/policies/privacy-policy
- Terms: https://www.alchemy.com/policies/terms
