---
description: Multi-chain portfolio (tokens + NFTs) for a wallet
argument-hint: "<address> [networks comma-separated]"
---

Build a multi-chain portfolio for the wallet in "$ARGUMENTS".

- Parse the address and optional comma-separated networks; default to a sensible set (e.g. `eth-mainnet`, `base-mainnet`, `polygon-mainnet`, `arb-mainnet`, `opt-mainnet`).
- Ensure an app is selected (`/alchemy:setup` if needed).
- Call `getTokenBalancesByAddress` for tokens with USD values across the chosen chains, and `getNFTsByAddress` for NFTs.

Present a per-chain summary plus a total estimated USD value. Keep it concise and flag truncation.
