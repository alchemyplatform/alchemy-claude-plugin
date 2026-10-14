# Alchemy

Query blockchain data across 100+ chains, simulate transactions, manage Alchemy
apps, and work with Solana — token balances & prices, NFTs, transfers,
transactions, and gas — directly in Claude Code. Tools are served by the hosted
[Alchemy MCP server](https://mcp.alchemy.com/mcp); authentication is OAuth via the
Alchemy Dashboard.

## Install

```bash
# In Claude Code:
/plugin marketplace add alchemyplatform/alchemy-claude-plugin
/plugin install alchemy@alchemy
```

## What's included

- **The Alchemy MCP server** (`https://mcp.alchemy.com/mcp`) with the data,
  simulation, tracing, Solana, and app-management tools.
- **Two skills:** `alchemy-mcp` for live work through the MCP tools, and
  `alchemy-api` for wiring Alchemy into application code with an API key.
- **Nine slash commands** (below). `/alchemy:create-app` is an administrative
  write that creates an Alchemy app; the other eight are read-only queries.

## What's excluded and why

This plugin reads blockchain data, simulates transactions, and administers your
Alchemy apps. It does not send transactions, swap, bridge, make payments, or sign
with a wallet, and its skills do not teach those flows. That keeps it read-only
with respect to your funds. The Alchemy MCP server also hides its faucet,
airdrop, and paymaster tools from this plugin.

Disclosure: `create_gas_policy` and `set_gas_policy_status` remain available.
They are administrative writes that configure or pause gas sponsorship policies
in your Alchemy account. They do not sign or broadcast transactions or move funds.

## Setup

1. Install the plugin and authenticate with Alchemy (OAuth) when prompted. If the
   browser does not open, run `/mcp` and select `alchemy`.
2. Run `/alchemy:setup` to list your apps and select one. This caches the app's
   API key for the rest of the session — required before most data tools.

If you already added `https://mcp.alchemy.com/mcp` to Claude Code by hand, remove
that entry with `claude mcp remove alchemy` so the plugin's entry and its
`x-alchemy-source` header apply. A user or project config with the same URL takes
precedence over the plugin's, and headers are not merged.

## Example prompts

Run `/alchemy:setup` once per session first.

1. **Prices:** "What are the current USD prices of ETH, USDC, and SOL?"
   Claude calls the Prices API tool and replies with a short table of spot prices.
2. **NFTs:** "List the NFTs owned by 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
   on Ethereum." Claude calls the NFT API and summarizes a sample grouped by
   collection, with the total count when available.
3. **App setup:** `/alchemy:setup`. Claude lists your Alchemy apps, asks which one
   to use if you have several (or selects the only one), and confirms the app now
   selected for the session.

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
| `/alchemy:create-app <name> <networks>` | Create a new Alchemy app (admin write) |

## Skills

Bundled skills help Claude use Alchemy correctly for both live agent work and
application code: `alchemy-mcp` and `alchemy-api`.

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
