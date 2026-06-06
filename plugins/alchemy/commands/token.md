---
description: Get price and metadata for a token
argument-hint: "<symbol or contract address> [network]"
---

Look up the token in "$ARGUMENTS".

- If the input is a symbol (e.g. ETH, USDC), call `getTokenPricesBySymbol`.
- If it's a contract address, call `getTokenPricesByAddress` (default network `eth-mainnet`) and `getTokenMetadata` for name/symbol/decimals/logo.
- An app must be selected first for address-based lookups (`/alchemy:setup` if needed). Symbol prices may work without a selected app.

Report the current price, 24h change if available, and key metadata.
