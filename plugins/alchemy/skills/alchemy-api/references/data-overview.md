---
id: references/data-overview.md
name: data-apis
description: Higher-level Alchemy APIs for asset discovery, wallet analytics, transfer history, NFT data, and token pricing. Use when you need indexed blockchain data without raw RPC log scanning, including token balances, NFT ownership, portfolio views, price feeds, and transaction simulation.
tags: []
related: []
updated: 2026-06-24
metadata:
  author: alchemyplatform
  version: "1.0"
---
# Data APIs

## Summary
Higher-level APIs for asset discovery, wallet analytics, transfer history, and pricing. These are optimized for analytics use cases and reduce the need for raw RPC log scanning.

## References (Recommended Order)
1. [data-token-api.md](data-token-api.md) - Token balances and token metadata for wallets and contracts.
2. [data-portfolio-apis.md](data-portfolio-apis.md) - Consolidated wallet views (tokens/NFTs/summary).
3. [data-transfers-api.md](data-transfers-api.md) - Transfer history and indexed movement data.
4. [data-nft-api.md](data-nft-api.md) - NFT ownership, metadata, and collection queries.
5. [data-prices-api.md](data-prices-api.md) - Token price data for current and historical pricing.
6. [data-simulation-api.md](data-simulation-api.md) - Pre-execution simulation for risk checks.
7. [data-stellar-api.md](data-stellar-api.md) - Stellar transfers, balances, and NFT holdings (native, classic trustlines, and Soroban contract tokens).

## How to Use This Skill
- Prefer these APIs when you want asset analytics or historical data without maintaining a custom indexer.
- If you need real-time updates, pair with `references/webhooks-overview.md`.

## Other ways to access this API

This file is part of the `alchemy-api` skill — for app code that ships with an Alchemy API key. Other paths to the same data:

- **Live agent work via MCP** (when MCP is wired into your client — see the `alchemy-mcp` skill). Call `select_app` first; tool names follow the API surface (e.g., `getTokenBalances`, `getNFTsForOwner`, `getTokenPricesBySymbol`, `getTokensByAddress`, `simulateAssetChanges`, `getAssetTransfers`). See per-surface reference files for the full tool list.

## Cross-References
- `references/node-enhanced-apis.md` for related RPC-style endpoints.
- `references/recipes-overview.md` for end-to-end workflows.
- `alchemy-mcp` skill for live agent work via the hosted MCP server.

## Official Docs
- [Data APIs Overview](https://www.alchemy.com/docs/reference/data-overview)
