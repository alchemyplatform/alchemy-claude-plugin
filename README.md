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

- **160+ MCP tools** from the hosted Alchemy MCP server (`mcp.alchemy.com`):
  EVM JSON-RPC, Token/NFT/Prices/Portfolio APIs, transaction simulation & tracing,
  and Solana (RPC + Digital Asset Standard).
- **Slash commands** for common workflows:
  `/alchemy:setup`, `/alchemy:balance`, `/alchemy:nfts`, `/alchemy:token`,
  `/alchemy:tx`, `/alchemy:portfolio`, `/alchemy:gas`, `/alchemy:solana`,
  `/alchemy:create-app`.
- **Skills** for using Alchemy in live agent work and in application code
  (`alchemy-mcp`, `alchemy-api`, `alchemy-cli`, `agentic-gateway`).

## Repository layout

```
.claude-plugin/marketplace.json   # marketplace entry
plugins/alchemy/                   # the plugin
  .claude-plugin/plugin.json       # plugin manifest
  .mcp.json                        # remote MCP server (mcp.alchemy.com)
  commands/                        # slash commands
  skills/                          # vendored Alchemy skills
scripts/sync-skills.sh             # refresh skills/ from alchemyplatform/skills
```

## Maintaining skills

The `skills/` directory is vendored from
[`alchemyplatform/skills`](https://github.com/alchemyplatform/skills) (the plugin
format requires components to live inside the plugin). Refresh them with:

```bash
./scripts/sync-skills.sh
```

## Support & legal

- Documentation: https://docs.alchemy.com/docs/alchemy-mcp-server
- Support: support@alchemy.com
- Privacy Policy: https://www.alchemy.com/policies/privacy-policy
- Terms: https://www.alchemy.com/policies/terms
