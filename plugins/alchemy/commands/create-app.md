---
description: Create a new Alchemy app
argument-hint: "<name> <networks comma-separated>"
---

Create a new Alchemy app from "$ARGUMENTS".

- Parse the app name and the list of networks.
- If networks are unclear, call `list_chains` to show valid network IDs/slugs and confirm with the user.
- Call `create_app` with the name and `chain_networks` (accepts Admin IDs like `ETH_MAINNET` or RPC slugs like `eth-mainnet`).

Confirm the new app's name and id, and remind the user the API key is viewable in the Alchemy Dashboard. Offer to `select_app` it for immediate use.
