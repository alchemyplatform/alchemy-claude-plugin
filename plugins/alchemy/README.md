# Alchemy

Query blockchain data across 100+ chains and manage Alchemy apps — token balances
& prices, NFTs, transfers, transactions, gas, and Solana — directly in Claude
Code. Tools are served by the hosted
[Alchemy MCP server](https://mcp.alchemy.com/mcp); authentication is OAuth via the
Alchemy Dashboard.

## Setup

1. Install the plugin and authenticate with Alchemy (OAuth) when prompted.
2. Run `/alchemy:setup` to list your apps and select one. This caches the app's
   API key for the rest of the session — required before most data tools.

## Slash commands

| Command | Description |
| --- | --- |
| `/alchemy:setup` | Connect and select an Alchemy app for this session |
| `/alchemy:balance <address> [network]` | Native + ERC-20 balances with USD values |
| `/alchemy:nfts <address> [network]` | NFTs owned by a wallet |
| `/alchemy:token <symbol\|address> [network]` | Token price + metadata |
| `/alchemy:tx <hash> [network]` | Transaction details + receipt |
| `/alchemy:portfolio <address> [networks]` | Multi-chain tokens + NFTs |
| `/alchemy:gas [network]` | Current gas / fee estimates |
| `/alchemy:solana <pubkey>` | SOL balance + SPL token accounts |
| `/alchemy:create-app <name> <networks>` | Create a new Alchemy app |

## Skills

Bundled skills help Claude use Alchemy correctly for both live agent work and
application code: `alchemy-mcp`, `alchemy-api`, `alchemy-cli`, and `agentic-gateway`.

## Privacy Policy

This plugin connects to Alchemy's hosted MCP server and APIs. Alchemy's data
collection, usage, retention, and sharing practices are described in the Alchemy
Privacy Policy: https://www.alchemy.com/policies/privacy-policy. The plugin itself
stores no data locally beyond what Claude Code persists for the connection; API
keys for a selected app are cached server-side for the session.

## Support

- Documentation: https://docs.alchemy.com/docs/alchemy-mcp-server
- Support: support@alchemy.com
- Terms of Service: https://www.alchemy.com/policies/terms
