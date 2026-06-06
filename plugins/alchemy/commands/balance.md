---
description: Show native + ERC-20 token balances (with USD) for a wallet
argument-hint: "<address> [network]"
---

Report token balances for the wallet in "$ARGUMENTS".

- Parse the address and optional network; default the network to `eth-mainnet`.
- Make sure an app is selected first. If not, call `list_apps` then `select_app` (or tell the user to run `/alchemy:setup`).
- Call `ethGetBalance` for the native coin balance.
- Call `getTokenBalances` for ERC-20 holdings; use `getTokenMetadata` to resolve missing symbols/decimals.
- Call `getTokenPricesBySymbol` (or `getTokenPricesByAddress`) to add USD values.

Present a concise table — asset, amount, USD value — sorted by USD value, and note if results were truncated.
