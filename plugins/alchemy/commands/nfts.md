---
description: List NFTs owned by a wallet
argument-hint: "<address> [network]"
---

List NFTs owned by the wallet in "$ARGUMENTS".

- Parse the address and optional network; default to `eth-mainnet`.
- Ensure an app is selected (run `/alchemy:setup` or call `list_apps` + `select_app` if needed).
- Call `getNFTsForOwner` with a reasonable `pageSize` (e.g. 20). Use pagination only if the user asks for more.

Summarize a sample: collection name, token id, and a short description. Group by collection and note the total count when available.
