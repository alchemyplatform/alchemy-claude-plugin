---
id: references/node-overview.md
name: node-apis
description: Core JSON-RPC and WebSocket APIs for EVM chains via Alchemy node endpoints, plus Debug/Trace and utility methods. Use when building EVM integrations that need standard RPC calls, real-time subscriptions, enhanced Alchemy methods, or execution-level tracing.
tags: []
related: []
updated: 2026-04-22
metadata:
  author: alchemyplatform
  version: "1.0"
---
# Node APIs (EVM)

## Summary
Core JSON-RPC and WebSocket APIs for EVM chains via Alchemy node endpoints, plus Debug/Trace and utility methods.

## References (Recommended Order)
1. [node-json-rpc.md](node-json-rpc.md) - Standard JSON-RPC methods and endpoint patterns.
2. [node-websocket-subscriptions.md](node-websocket-subscriptions.md) - Real-time subscriptions (pending txs, logs, new heads).
3. [node-enhanced-apis.md](node-enhanced-apis.md) - Alchemy-enhanced RPC methods that reduce RPC call count.
4. [node-utility-api.md](node-utility-api.md) - Convenience endpoints like bulk transaction receipts.
5. [node-debug-api.md](node-debug-api.md) - Debug tracing for transaction simulation and execution insight.
6. [node-trace-api.md](node-trace-api.md) - Trace-level details for internal calls and state diffs.

## Recently Added / Updated Chains
- **Injective** — Cosmos SDK-based L1 with full EVM compatibility. Supports standard `eth_*` JSON-RPC methods. Use endpoint pattern `injective-mainnet`. A few methods (`eth_getBlockReceipts`, `eth_syncing`, `net_listening`) are testnet-only today. Debug namespace (`debug_*`) methods are served by the standalone **Debug API product**, not the chain spec — see [Debug API Quickstart](https://www.alchemy.com/docs/reference/debug-api-quickstart). Overview: [Injective API Overview](https://www.alchemy.com/docs/chains/injective/injective-api-overview).
- **Gensyn** — mainnet is live. Endpoint `gensyn-mainnet` (chain ID `685689`); `gensyn-testnet` remains available. See the [Gensyn quickstart](https://www.alchemy.com/docs/chains/gensyn/gensyn-api-quickstart).
- **MegaETH** — supports `eth_getWithdrawalProof` (20 CU). See [Compute Unit Costs](https://www.alchemy.com/docs/reference/compute-unit-costs#megaeth-specific-methods).

## Recently Deprecated Chains
- **Arbitrum Nova** — deprecated. Nova endpoints are no longer supported; see the [Arbitrum Nova deprecation notice](https://www.alchemy.com/docs/reference/arbitrum-nova/arbitrum-nova-deprecation-notice).

## How to Use This Skill
- Start with `node-json-rpc.md` for base connectivity and request patterns.
- Use `node-enhanced-apis.md` for wallet/asset analytics on EVM without scanning logs.
- Use Debug/Trace when you need internal call trees or detailed execution flow.

## Other ways to access this API

This file is part of the `alchemy-api` skill — for app code that ships with an Alchemy API key. Other paths to the same data:

- **Live agent work via MCP** (when MCP is wired into your client — see the `alchemy-mcp` skill). Call `select_app` first, then any of:
  `ethBlockNumber`, `ethGetBalance`, `ethGetTransactionByHash`, `ethGetBlockByNumber`, `ethGasPrice`, `ethGetLogs` (full list in the `alchemy-mcp` skill catalog).

## Cross-References
- `references/data-overview.md` for higher-level asset analytics.
- `references/webhooks-overview.md` for event-driven flows.
- `references/operational-auth-and-keys.md`, `references/operational-rate-limits-and-compute-units.md`, and `references/operational-best-practices.md` for auth, limits, and reliability.
- `alchemy-mcp` skill for live agent work via the hosted MCP server.

## Official Docs
- [Chain APIs Overview](https://www.alchemy.com/docs/reference/chain-apis-overview)
- [Enhanced APIs Overview](https://www.alchemy.com/docs/reference/enhanced-apis-overview)
