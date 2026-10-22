---
name: alchemy-api
description: Wire Alchemy into application code (server, backend, dApp, script) using a standard API key. Preferred app-integration path for normal server/backend usage. Covers EVM JSON-RPC, Token API, NFT API, Transfers API, Prices API, Portfolio API, Simulation, Webhooks, Solana RPC, Solana DAS, Solana Yellowstone gRPC, Sui gRPC, and operational topics. Requires `$ALCHEMY_API_KEY`. For live agent work in this session (querying, admin, local automation), use `alchemy-mcp` instead. No API key yet? Copy one from the Alchemy Dashboard (https://dashboard.alchemy.com), or use `alchemy-mcp` for live work in this session (OAuth sign-in, no key needed).
license: MIT
compatibility: Requires network access and `$ALCHEMY_API_KEY` environment variable. Works across Claude.ai, Claude Code, Cursor, Codex, and API.
metadata:
  author: alchemyplatform
  version: "2.0"
---
# Alchemy API (with API Key)

Reference and integration guide for wiring Alchemy APIs into application code using a standard API key. This file alone is enough to ship a basic integration; the `references/` directory contains deeper coverage of every product surface.

## When to use this skill

Use `alchemy-api` when **all** of the following are true:

- The user is wiring Alchemy into **application code** (server, backend, dApp, worker, script) that runs **outside** the current agent session
- They have, or are willing to create, an Alchemy API key (free at [dashboard.alchemy.com](https://dashboard.alchemy.com/))

This is the **preferred app-integration path** for normal server/backend usage.

## When to use a different skill

| Situation | Use this skill instead |
| --- | --- |
| Live agent work in this session (queries, admin, on-machine automation); no API key needed, sign in with OAuth | `alchemy-mcp` |

Do **not** use this skill to run ad-hoc live queries from inside the agent session — that's the `alchemy-mcp` path. This skill is for code that ships.

## Mandatory preflight gate

Before writing application code or making any network call:

1. Confirm the user is building **application code** (not asking the agent to run a live query). If the user is asking for live work, redirect to `alchemy-mcp`.
2. Check `$ALCHEMY_API_KEY` is set without printing it (e.g. `[ -n "$ALCHEMY_API_KEY" ] && echo set || echo missing`).
3. If `$ALCHEMY_API_KEY` is unset or empty, take the first of these that applies:
   - For live work in this session, use the `alchemy-mcp` skill (the bundled Alchemy MCP server signs in with OAuth, no API key needed), **or**
   - For application code, tell the user they can create a free API key at [https://dashboard.alchemy.com/](https://dashboard.alchemy.com/) and copy it into `ALCHEMY_API_KEY`.

You MUST NOT call any keyless or public fallback (including `.../v2/demo`) unless the user explicitly asks for that endpoint. No public RPC endpoints (publicnode, llamarpc, cloudflare-eth, etc.) as a fallback.

## Summary

A self-contained guide for AI agents integrating Alchemy APIs using an API key. This file alone should be enough to ship a basic integration. Use the reference files for depth, edge cases, and advanced workflows.

Developers can always create a free API key at [https://dashboard.alchemy.com/](https://dashboard.alchemy.com/).

## Do this first

1. Confirm app-integration scope (see [Mandatory preflight gate](#mandatory-preflight-gate)).
2. Choose the right product using the [Endpoint selector](#endpoint-selector-top-tasks) below.
3. Use the [Base URLs + auth](#base-urls--auth-cheat-sheet) table for the correct endpoint and headers.
4. Copy a [Quickstart example](#one-file-quickstart-copypaste) and test against a testnet first.

## Base URLs + auth (cheat sheet)
| Product | Base URL | Auth | Notes |
| --- | --- | --- | --- |
| Ethereum RPC (HTTPS) | `https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | Standard EVM reads and writes. |
| Ethereum RPC (WSS) | `wss://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | Subscriptions and realtime. |
| Base RPC (HTTPS) | `https://base-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | EVM L2. |
| Base RPC (WSS) | `wss://base-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | Subscriptions and realtime. |
| Arbitrum RPC (HTTPS) | `https://arb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | EVM L2. |
| Arbitrum RPC (WSS) | `wss://arb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | Subscriptions and realtime. |
| BNB RPC (HTTPS) | `https://bnb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | EVM L1. |
| BNB RPC (WSS) | `wss://bnb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | Subscriptions and realtime. |
| Solana RPC (HTTPS) | `https://solana-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | API key in URL | Solana JSON-RPC. |
| Solana Yellowstone gRPC | `https://solana-mainnet.g.alchemy.com` | `X-Token: $ALCHEMY_API_KEY` | gRPC streaming (Yellowstone). |
| Sui gRPC | `sui-mainnet.g.alchemy.com:443` | `Authorization: Bearer $ALCHEMY_API_KEY` | Sui gRPC API (objects, txs, balances, streaming). |
| NFT API | `https://<network>.g.alchemy.com/nft/v3/$ALCHEMY_API_KEY` | API key in URL | NFT ownership and metadata. |
| Prices API | `https://api.g.alchemy.com/prices/v1/$ALCHEMY_API_KEY` | API key in URL | Prices by symbol or address. |
| Portfolio API | `https://api.g.alchemy.com/data/v1/$ALCHEMY_API_KEY` | API key in URL | Multi-chain wallet views. |
| Notify API | `https://dashboard.alchemy.com/api` | `X-Alchemy-Token: <ALCHEMY_NOTIFY_AUTH_TOKEN>` | Generate token in dashboard. |

## Endpoint selector (top tasks)
| You need | Use this | Skill / file |
| --- | --- | --- |
| EVM read/write | JSON-RPC `eth_*` | `references/node-json-rpc.md` |
| Realtime events | `eth_subscribe` | `references/node-websocket-subscriptions.md` |
| Token balances | `alchemy_getTokenBalances` | `references/data-token-api.md` |
| Token metadata | `alchemy_getTokenMetadata` | `references/data-token-api.md` |
| Transfers history | `alchemy_getAssetTransfers` | `references/data-transfers-api.md` |
| NFT ownership | `GET /getNFTsForOwner` | `references/data-nft-api.md` |
| NFT metadata | `GET /getNFTMetadata` | `references/data-nft-api.md` |
| Prices (spot) | `GET /tokens/by-symbol` | `references/data-prices-api.md` |
| Prices (historical) | `POST /tokens/historical` | `references/data-prices-api.md` |
| Portfolio (multi-chain) | `POST /assets/*/by-address` | `references/data-portfolio-apis.md` |
| Simulate tx | `alchemy_simulateAssetChanges` | `references/data-simulation-api.md` |
| Create webhook | `POST /create-webhook` | `references/webhooks-details.md` |
| Solana NFT data | `getAssetsByOwner` (DAS) | `references/solana-das-api.md` |
| Solana realtime events (per-account / per-program / logs / tx status) | `accountSubscribe`, `programSubscribe`, `logsSubscribe`, `signatureSubscribe` (PubSub WebSocket) | `references/solana-websocket-subscriptions.md` |
| Sui objects/txs | `GetObject`, `GetTransaction` (gRPC) | `references/sui-grpc-objects-and-ledger.md` |
| Sui balances | `GetBalance`, `ListBalances` (gRPC) | `references/sui-grpc-state-and-balances.md` |
| Sui checkpoints stream | `SubscribeCheckpoints` (gRPC) | `references/sui-grpc-subscriptions.md` |

## One-file quickstart (copy/paste)

> **No API key?** For live work in this session, use the bundled Alchemy MCP server (sign in with OAuth). Its `list_apps` and `select_app` tools (or `create_app`, then `select_app`) choose the app the MCP uses, but they don't reveal raw keys. For application code, copy your API key from the Alchemy Dashboard (https://dashboard.alchemy.com) into `ALCHEMY_API_KEY`.

### EVM JSON-RPC (read)
```bash
curl -s https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'
```

### Token balances
```bash
curl -s https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"alchemy_getTokenBalances","params":["0x00000000219ab540356cbb839cbe05303d7705fa"]}'
```

### Transfer history
```bash
curl -s https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"alchemy_getAssetTransfers","params":[{"fromBlock":"0x0","toBlock":"latest","toAddress":"0x00000000219ab540356cbb839cbe05303d7705fa","category":["erc20"],"withMetadata":true,"maxCount":"0x3e8"}]}'
```

### NFT ownership
```bash
curl -s "https://eth-mainnet.g.alchemy.com/nft/v3/YOUR_API_KEY/getNFTsForOwner?owner=0x00000000219ab540356cbb839cbe05303d7705fa"
```

### Prices (spot)
```bash
curl -s "https://api.g.alchemy.com/prices/v1/YOUR_API_KEY/tokens/by-symbol?symbols=ETH&symbols=USDC"
```

### Prices (historical)
```bash
curl -s -X POST "https://api.g.alchemy.com/prices/v1/YOUR_API_KEY/tokens/historical" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"ETH","startTime":"2024-01-01T00:00:00Z","endTime":"2024-01-02T00:00:00Z"}'
```

### Create Notify webhook
```bash
curl -s -X POST "https://dashboard.alchemy.com/api/create-webhook" \
  -H "Content-Type: application/json" \
  -H "X-Alchemy-Token: <ALCHEMY_NOTIFY_AUTH_TOKEN>" \
  -d '{"network":"ETH_MAINNET","webhook_type":"ADDRESS_ACTIVITY","webhook_url":"https://example.com/webhook","addresses":["0x00000000219ab540356cbb839cbe05303d7705fa"]}'
```

### Verify webhook signature (Node)
```ts
import crypto from "crypto";

export function verify(rawBody: string, signature: string, secret: string) {
  const hmac = crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
  return crypto.timingSafeEqual(Buffer.from(hmac), Buffer.from(signature));
}
```

## Network naming rules
- Data APIs and JSON-RPC use lowercase network enums like `eth-mainnet`.
- Notify API uses uppercase enums like `ETH_MAINNET`.

## Pagination + limits (cheat sheet)
| Endpoint | Limit | Notes |
| --- | --- | --- |
| `alchemy_getTokenBalances` | `maxCount` <= 100 | Use `pageKey` for pagination. |
| `alchemy_getAssetTransfers` | `maxCount` default `0x3e8` | Use `pageKey` for pagination. |
| Portfolio token balances | 3 address/network pairs, 20 networks total | `pageKey` supported. |
| Portfolio NFTs | 2 address/network pairs, 15 networks each | `pageKey` supported. |
| Prices by address | 25 addresses, 3 networks | POST body `addresses[]`. |
| Transactions history (beta) | 1 address/network pair, 2 networks | ETH and BASE mainnets only. |

## Common token addresses
| Token | Chain | Address |
| --- | --- | --- |
| ETH | ethereum | `0x0000000000000000000000000000000000000000` |
| WETH | ethereum | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` |
| USDC | ethereum | `0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eB48` |
| USDC | base | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |

## Failure modes + retries
- HTTP `429` means rate limit. Use exponential backoff with jitter.
- JSON-RPC errors come in `error` fields even with HTTP 200.
- Use `pageKey` to resume pagination after failures.
- De-dupe websocket events on reconnect.

## Skill map

For the complete index of all 60+ reference files organized by product area (Node, Data, Webhooks, Solana, Sui gRPC, Rollups, Recipes, Operational), see `references/skill-map.md`.

Quick category overview:
- **Node**: JSON-RPC, WebSocket, Debug, Trace, Enhanced APIs, Utility
- **Data**: NFT, Portfolio, Prices, Simulation, Token, Transfers
- **Webhooks**: Address Activity, Custom (GraphQL), NFT Activity, Payloads, Signatures
- **Solana**: JSON-RPC, DAS, Yellowstone gRPC (streaming)
- **Sui gRPC**: Objects, Balances, Move Packages, Name Service, Subscriptions, Signature Verification
- **Rollups**: L2/L3 deployment overview
- **Recipes**: 10 end-to-end integration workflows
- **Operational**: Auth, Rate Limits, Monitoring, Best Practices

## Handing off to other skills

| The user wants to... | Hand off to |
| --- | --- |
| Run a one-off live query, admin command, or on-machine automation in this session | `alchemy-mcp` |

## Troubleshooting

### API key not working
- Verify `$ALCHEMY_API_KEY` is set without printing it: `[ -n "$ALCHEMY_API_KEY" ] && echo set || echo missing`
- Confirm the key is valid at [dashboard.alchemy.com](https://dashboard.alchemy.com/)
- Check if allowlists restrict the key to specific IPs/domains

### HTTP 429 (rate limited)
- Use exponential backoff with jitter before retrying
- Check your compute unit budget in the Alchemy dashboard
- See `references/operational-rate-limits-and-compute-units.md` for limits per plan

### Wrong network slug
- Data APIs and JSON-RPC use lowercase: `eth-mainnet`, `base-mainnet`
- Notify API uses uppercase: `ETH_MAINNET`, `BASE_MAINNET`
- See `references/operational-supported-networks.md` for the full list

### JSON-RPC error with HTTP 200
- Alchemy returns JSON-RPC errors inside the `error` field even with a 200 status code
- Always check `response.error` in addition to HTTP status

## Official links
- [Developer docs](https://www.alchemy.com/docs)
- [Get Started guide](https://www.alchemy.com/docs/get-started)
- [Create a free API key](https://dashboard.alchemy.com/)
