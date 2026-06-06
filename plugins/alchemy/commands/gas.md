---
description: Show current gas / fee estimates for a network
argument-hint: "[network]"
---

Report current gas conditions for the network in "$ARGUMENTS" (default `eth-mainnet`).

- Ensure an app is selected (`/alchemy:setup` if needed).
- Call `ethGasPrice` for the current gas price, `ethMaxPriorityFeePerGas` for the priority fee, and `ethFeeHistory` for recent base-fee trend.

Present gwei values for base fee, priority fee, and a suggested max fee, with a one-line read on whether gas is currently low/normal/high.
