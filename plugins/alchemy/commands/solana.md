---
description: Show SOL balance and token accounts for a Solana wallet
argument-hint: "<pubkey>"
---

Report Solana holdings for the address in "$ARGUMENTS".

- Use network `solana-mainnet`.
- Ensure an app is selected with Solana enabled (`/alchemy:setup` if needed).
- Call `solana_getBalance` for the SOL balance (convert lamports → SOL) and `solana_getTokenAccountsByOwner` for SPL token accounts.

Summarize the SOL balance and a sample of token accounts (mint, amount). Note if the selected app doesn't have Solana enabled.
