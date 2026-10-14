---
id: references/solana-overview.md
name: solana
description: Solana-specific APIs including standard JSON-RPC, Digital Asset Standard (DAS) for NFTs and compressed assets. Use when building Solana applications that need RPC access or NFT/asset queries. For high-throughput streaming, see `references/solana-grpc-overview.md`.
tags: []
related: []
updated: 2026-05-06
metadata:
  author: alchemyplatform
  version: "1.0"
---
# Solana APIs

## Summary
Solana-specific APIs and streaming endpoints, including DAS (Digital Asset Standard), PubSub WebSocket subscriptions, and Yellowstone gRPC.

## References (Recommended Order)
1. [solana-rpc.md](solana-rpc.md) - Standard Solana JSON-RPC usage patterns.
2. [solana-das-api.md](solana-das-api.md) - DAS endpoints for assets and metadata.
3. [solana-websocket-subscriptions.md](solana-websocket-subscriptions.md) - PubSub WebSocket subscriptions (`accountSubscribe`, `programSubscribe`, `logsSubscribe`, etc.).

## Cross-References
- `references/solana-grpc-overview.md` for high-throughput streaming (accounts/transactions/blocks).
- `references/data-overview.md` for EVM assets.
- `alchemy-mcp` skill for live agent work via the hosted MCP server. Exposes 50+ Solana RPC tools and DAS tools.

## Official Docs
- [Solana API Quickstart](https://www.alchemy.com/docs/reference/solana-api-quickstart)
- [DAS APIs for Solana](https://www.alchemy.com/docs/reference/alchemy-das-apis-for-solana)
