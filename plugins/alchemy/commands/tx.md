---
description: Look up a transaction's details and receipt
argument-hint: "<tx hash> [network]"
---

Look up the transaction in "$ARGUMENTS".

- Parse the tx hash and optional network; default to `eth-mainnet`.
- Ensure an app is selected (`/alchemy:setup` if needed).
- Call `ethGetTransactionByHash` for the transaction and `ethGetTransactionReceipt` for status, gas used, and logs.

Summarize: from, to, value, status (success/failed), gas used, block number, and notable log/event activity. If the hash is not found, say so and double-check the network.
