# Alchemy for Cursor

Connects Cursor to Alchemy's hosted MCP server (https://mcp.alchemy.com/mcp) for blockchain data across 100+ chains.

## What you get

- Balances, token prices and metadata, NFT ownership and floor prices, multi-chain portfolios, asset transfers and receipts
- Transaction simulation and EVM tracing
- Solana RPC and DAS queries
- Management of your own Alchemy apps, API-key allowlists, webhooks, Gas Manager policies and usage reports

## What it does not do

It does not hold wallet keys and has no tool that signs, sends or broadcasts transactions. It cannot move funds.

## Setup

1. Install the plugin. Cursor opens an Alchemy sign-in page on first use (OAuth). No API key is needed.
2. Ask: "Show me my Alchemy apps", then pick one with `select_app`. RPC and data tools need an app selected.
3. Try: "What is the ETH and USDC price right now?" or "List the NFTs owned by <address> on Ethereum, excluding spam."

## Cost

Installing and connecting is free. Usage counts against your Alchemy plan; a free plan is available.

## Attribution

Requests from this plugin send the header `x-alchemy-source: cursor-marketplace`, an install-source tag. It carries no user data.

## Links

Docs: https://docs.alchemy.com/docs/alchemy-mcp-server. Privacy: https://www.alchemy.com/policies/privacy-policy. Terms: https://www.alchemy.com/policies/terms. Support: https://www.alchemy.com/support
