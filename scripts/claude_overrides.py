#!/usr/bin/env python3
"""Apply the Claude Code directory overrides to the vendored Alchemy skills.

Usage: claude_overrides.py [--commands DIR] [--verbose] SKILLS_DIR

SKILLS_DIR is a staging copy of the pinned alchemyplatform/skills skills
(see scripts/sync-skills.sh). The script is all-or-nothing: every operation,
the forbidden-content scan and the reference check run in memory, and files are
only written once all of them pass. A tree that already carries the
.claude-overrides-applied marker is refused before anything is read or changed.

Every operation declares an exact expected match count. A mismatch exits 1
naming the file, the anchor and the counts: upstream changed, update the
override. Python 3 standard library only.
"""

import argparse
import fnmatch
import os
import re
import sys

MARKER = ".claude-overrides-applied"
MARKER_TEXT = (
    "Applied by scripts/claude_overrides.py.\n"
    "Do not run it again on this tree; re-run scripts/sync-skills.sh instead.\n"
)

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s")
LIST_ITEM_RE = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+")
FENCED_SHELL = ("bash", "sh", "shell")


class OverrideError(Exception):
    pass


def op(kind, path, **args):
    return {"kind": kind, "path": path, "args": args}


def remove_file(path):
    return op("remove_file", path)


def remove_glob(pattern, count):
    return op("remove_glob", pattern, count=count)


def remove_section(path, heading_line):
    return op("remove_section", path, heading=heading_line)


def remove_lines(path, snippet, count):
    return op("remove_lines", path, snippet=snippet, count=count)


def remove_list_item(path, snippet, count):
    return op("remove_list_item", path, snippet=snippet, count=count)


def replace(path, old, new, count):
    return op("replace", path, old=old, new=new, count=count)


def replace_in_fences(path, old, new, count, langs=FENCED_SHELL):
    return op("replace_in_fences", path, old=old, new=new, count=count, langs=langs)


def set_frontmatter_scalar(path, key, value):
    return op("set_frontmatter_scalar", path, key=key, value=value)


# ---------------------------------------------------------------------------
# Declarative operations
# ---------------------------------------------------------------------------

API = "alchemy-api"
MCP = "alchemy-mcp"
REF = f"{API}/references"

# Files whose "Other ways to access this API" section carries a CLI bullet, an
# MCP bullet and an x402/MPP bullet.
OTHER_WAYS_FILES = [
    f"{REF}/data-nft-api.md",
    f"{REF}/data-overview.md",
    f"{REF}/data-portfolio-apis.md",
    f"{REF}/data-prices-api.md",
    f"{REF}/data-simulation-api.md",
    f"{REF}/data-token-api.md",
    f"{REF}/data-transfers-api.md",
    f"{REF}/node-enhanced-apis.md",
    f"{REF}/node-json-rpc.md",
    f"{REF}/node-overview.md",
]

# Retained bash examples that expand $ALCHEMY_API_KEY from the host
# environment. Counts are taken after the removals above them have run.
FENCED_API_KEY_COUNTS = {
    f"{API}/SKILL.md": 6,
    f"{REF}/data-nft-api.md": 6,
    f"{REF}/data-portfolio-apis.md": 5,
    f"{REF}/data-prices-api.md": 4,
    f"{REF}/data-simulation-api.md": 4,
    f"{REF}/data-stellar-api.md": 3,
    f"{REF}/data-token-api.md": 3,
    f"{REF}/data-transfers-api.md": 1,
    f"{REF}/node-debug-api.md": 3,
    f"{REF}/node-enhanced-apis.md": 1,
    f"{REF}/node-json-rpc.md": 6,
    f"{REF}/node-trace-api.md": 4,
    f"{REF}/node-utility-api.md": 1,
    f"{REF}/recipes-get-nft-metadata.md": 1,
    f"{REF}/recipes-get-nft-ownership.md": 1,
    f"{REF}/recipes-get-portfolio.md": 3,
    f"{REF}/recipes-get-prices-current-historical.md": 2,
    f"{REF}/recipes-get-token-balances.md": 1,
    f"{REF}/recipes-get-token-metadata.md": 1,
    f"{REF}/recipes-get-transfers-history.md": 1,
    f"{REF}/recipes-simulate-transaction.md": 1,
    f"{REF}/solana-das-api.md": 6,
    f"{REF}/solana-rpc.md": 4,
}

MCP_DESCRIPTION = (
    "Use the Alchemy MCP server (`https://mcp.alchemy.com/mcp`) for live blockchain data "
    "and admin work when MCP is wired into your AI client. Exposes 150+ tools across 100+ "
    "chains for token prices, NFT metadata, transactions, simulation, tracing, account "
    "abstraction, Solana DAS, and app management. Use for live querying, analysis, admin "
    "work, or on-machine agent work — not for application code that ships to production. "
    "For application code, use the `alchemy-api` skill (with an Alchemy API key)."
)

MCP_COMPATIBILITY = (
    "Requires the Alchemy MCP server connection provided by this plugin (OAuth sign-in "
    "with your Alchemy account; no API key or local install required)."
)

API_DESCRIPTION = (
    "Wire Alchemy into application code (server, backend, dApp, script) using a standard "
    "API key. Preferred app-integration path for normal server/backend usage. Covers EVM "
    "JSON-RPC, Token API, NFT API, Transfers API, Prices API, Portfolio API, Simulation, "
    "Webhooks, Solana RPC, Solana DAS, Solana Yellowstone gRPC, Sui gRPC, and operational "
    "topics. Requires `$ALCHEMY_API_KEY`. For live agent work in this session (querying, "
    "admin, local automation), use `alchemy-mcp` instead. No API key yet? Copy one from "
    "the Alchemy Dashboard (https://dashboard.alchemy.com), or use `alchemy-mcp` for live "
    "work in this session (OAuth sign-in, no key needed)."
)

NO_KEY_CALLOUT_OLD = (
    "> **No API key?** Use the `agentic-gateway` skill instead. Replace API-key URLs with "
    "`https://x402.alchemy.com/eth-mainnet/v2` and add `Authorization: SIWE <token>` "
    "(or `SIWS <token>` for a Solana wallet). See the `agentic-gateway` skill for setup."
)

NO_KEY_CALLOUT_NEW = (
    "> **No API key?** For live work in this session, use the bundled Alchemy MCP server "
    "(sign in with OAuth). Its `list_apps` and `select_app` tools (or `create_app`, then "
    "`select_app`) choose the app the MCP uses, but they don't reveal raw keys. For "
    "application code, copy your API key from the Alchemy Dashboard "
    "(https://dashboard.alchemy.com) into `ALCHEMY_API_KEY`."
)

KEY_CHECK = '`[ -n "$ALCHEMY_API_KEY" ] && echo set || echo missing`'

SOLANA_WALLET_DESC_OLD = (
    " compressed assets, and wallet integration. Use when building Solana applications "
    "that need RPC access, NFT/asset queries, or Solana wallet tooling."
)
SOLANA_WALLET_DESC_NEW = (
    " compressed assets. Use when building Solana applications that need RPC access or "
    "NFT/asset queries."
)

SKILL_MAP = f"{REF}/skill-map.md"
MISSING_OPERATIONAL_ROWS = [
    "operational-overview.md",
    "operational-alerts.md",
    "operational-allowlists.md",
    "operational-dashboard-tools.md",
    "operational-pricing-and-plans.md",
    "operational-request-logs.md",
    "operational-roles-and-sso.md",
    "operational-sandbox.md",
]

OPERATIONS = [
    # -- Codex agent metadata ------------------------------------------------
    remove_file(f"{API}/agents/openai.yaml"),
    remove_file(f"{MCP}/agents/openai.yaml"),
    # -- Fund-moving and signing content: whole files --------------------------
    remove_glob(f"{REF}/wallets-*.md", 9),
    remove_file(f"{REF}/solana-wallets.md"),
    remove_file(f"{REF}/sui-grpc-transactions.md"),
    # =========================================================================
    # alchemy-mcp/SKILL.md
    # =========================================================================
    set_frontmatter_scalar(f"{MCP}/SKILL.md", "description", MCP_DESCRIPTION),
    set_frontmatter_scalar(f"{MCP}/SKILL.md", "compatibility", MCP_COMPATIBILITY),
    replace(
        f"{MCP}/SKILL.md",
        "- An MCP-compatible client (Claude Code, Codex, Cursor, Claude Desktop, VS Code "
        "Copilot, etc.) is already wired against `https://mcp.alchemy.com/mcp`, OR the "
        "user is willing to add it\n",
        "- The Alchemy MCP server (`https://mcp.alchemy.com/mcp`) is connected in this "
        "session (the Alchemy plugin provides the connection)\n",
        1,
    ),
    remove_lines(f"{MCP}/SKILL.md", "- The Alchemy CLI (`@alchemy/cli`) is **not** installed locally", 1),
    remove_lines(
        f"{MCP}/SKILL.md",
        "If the CLI is installed locally — or if both CLI and MCP are available — prefer "
        "the `alchemy-cli` skill instead.",
        1,
    ),
    remove_lines(
        f"{MCP}/SKILL.md",
        "| `@alchemy/cli` is installed locally, or both CLI and MCP are available | `alchemy-cli` |",
        1,
    ),
    remove_lines(f"{MCP}/SKILL.md", "| Neither CLI nor MCP is available |", 1),
    replace(
        f"{MCP}/SKILL.md",
        "| Building application code without an API key, or as an autonomous agent that "
        "needs to pay for itself, or you explicitly want x402/MPP | `agentic-gateway` |",
        "| Building application code and you don't have an API key yet | `alchemy-api` "
        "(copy a key from the Alchemy Dashboard, https://dashboard.alchemy.com) |",
        1,
    ),
    replace(
        f"{MCP}/SKILL.md",
        "and the Alchemy agent skills in one install:",
        "and the `alchemy-mcp` and `alchemy-api` skills in one install:",
        1,
    ),
    replace(
        f"{MCP}/SKILL.md",
        "\nTo wire just the MCP server without the plugin, use the manual command:\n\n"
        "```bash\nclaude mcp add alchemy --transport http https://mcp.alchemy.com/mcp\n```\n\n"
        "Restart Claude Code, then run `/mcp` and select `alchemy` to authenticate.\n",
        "",
        1,
    ),
    remove_section(f"{MCP}/SKILL.md", "### Codex"),
    remove_section(f"{MCP}/SKILL.md", "### Cursor"),
    remove_section(f"{MCP}/SKILL.md", "### Claude Desktop"),
    remove_section(f"{MCP}/SKILL.md", "### VS Code Copilot"),
    remove_section(f"{MCP}/SKILL.md", "### Any other MCP client"),
    replace(f"{MCP}/SKILL.md", "call any of the 159 tools", "call any of the 150+ tools", 1),
    replace(
        f"{MCP}/SKILL.md",
        'create_app(name="My App", networks=["eth-mainnet", "base-mainnet"])',
        'create_app(name="My App", chain_networks=["eth-mainnet", "base-mainnet"])',
        1,
    ),
    replace(
        f"{MCP}/SKILL.md",
        "The server exposes **159 tools** across three categories.",
        "The server exposes **150+ tools** across three categories.",
        1,
    ),
    replace(f"{MCP}/SKILL.md", "### RPC (123 tools)", "### RPC (120 tools)", 1),
    replace(
        f"{MCP}/SKILL.md",
        "| ERC-4337 Account Abstraction | 7 | `estimateUserOperationGas`, "
        "`getUserOperationReceipt`, `requestGasAndPaymasterAndData` |",
        "| ERC-4337 Account Abstraction | 5 | `estimateUserOperationGas`, "
        "`getUserOperationReceipt`, `getUserOperationByHash` |",
        1,
    ),
    replace(f"{MCP}/SKILL.md", "| Solana Standard RPC | 50 |", "| Solana Standard RPC | 49 |", 1),
    replace(
        f"{MCP}/SKILL.md",
        "hand off to `alchemy-api` (with API key) or `agentic-gateway` (without).",
        "hand off to `alchemy-api` (copy your API key from the Alchemy Dashboard).",
        1,
    ),
    # =========================================================================
    # alchemy-api/SKILL.md
    # =========================================================================
    set_frontmatter_scalar(f"{API}/SKILL.md", "description", API_DESCRIPTION),
    remove_lines(
        f"{API}/SKILL.md",
        "| Live agent work in this session (queries, admin, on-machine automation) and "
        "`@alchemy/cli` is installed locally",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "| Live agent work in this session and only MCP is wired into the client (no CLI) | `alchemy-mcp` |",
        "| Live agent work in this session (queries, admin, on-machine automation); no API "
        "key needed, sign in with OAuth | `alchemy-mcp` |",
        1,
    ),
    remove_lines(f"{API}/SKILL.md", "| Live agent work and neither is available |", 1),
    remove_lines(
        f"{API}/SKILL.md",
        "| Application code without an API key — autonomous agent paying per-request",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "that's the `alchemy-cli` / `alchemy-mcp` path.",
        "that's the `alchemy-mcp` path.",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "redirect to `alchemy-cli` (preferred) or `alchemy-mcp`.",
        "redirect to `alchemy-mcp`.",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "2. Check `$ALCHEMY_API_KEY` is set (e.g. `echo $ALCHEMY_API_KEY`).",
        f"2. Check `$ALCHEMY_API_KEY` is set without printing it (e.g. {KEY_CHECK}).",
        1,
    ),
    remove_lines(f"{API}/SKILL.md", "**CLI bridge (recommended if `@alchemy/cli` is installed locally):**", 1),
    replace(
        f"{API}/SKILL.md",
        "   - Tell the user they can create a free API key at "
        "[https://dashboard.alchemy.com/](https://dashboard.alchemy.com/), **or**\n"
        "   - Switch to the `agentic-gateway` skill (x402/MPP gateway, wallet-based auth, "
        "no API key needed).\n",
        "   - For live work in this session, use the `alchemy-mcp` skill (the bundled "
        "Alchemy MCP server signs in with OAuth, no API key needed), **or**\n"
        "   - For application code, tell the user they can create a free API key at "
        "[https://dashboard.alchemy.com/](https://dashboard.alchemy.com/) and copy it into "
        "`ALCHEMY_API_KEY`.\n",
        1,
    ),
    remove_section(f"{API}/SKILL.md", "### Bridging from the CLI to an API key"),
    replace(f"{API}/SKILL.md", NO_KEY_CALLOUT_OLD, NO_KEY_CALLOUT_NEW, 1),
    replace(
        f"{API}/SKILL.md",
        '-H "X-Alchemy-Token: $ALCHEMY_NOTIFY_AUTH_TOKEN"',
        '-H "X-Alchemy-Token: <ALCHEMY_NOTIFY_AUTH_TOKEN>"',
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "all 90+ reference files organized by product area (Node, Data, Webhooks, Solana, "
        "Sui gRPC, Wallets, Rollups, Recipes, Operational, Ecosystem)",
        "all 60+ reference files organized by product area (Node, Data, Webhooks, Solana, "
        "Sui gRPC, Rollups, Recipes, Operational)",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "- **Solana**: JSON-RPC, DAS, Yellowstone gRPC (streaming), Wallets",
        "- **Solana**: JSON-RPC, DAS, Yellowstone gRPC (streaming)",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "- **Sui gRPC**: Objects, Transactions, Balances,",
        "- **Sui gRPC**: Objects, Balances,",
        1,
    ),
    remove_lines(f"{API}/SKILL.md", "- **Wallets**: Account Kit, Bundler, Gas Manager,", 1),
    remove_lines(f"{API}/SKILL.md", "- **Ecosystem**: viem, ethers, wagmi,", 1),
    remove_lines(
        f"{API}/SKILL.md",
        "| Run a one-off live query, admin command, or on-machine automation in this "
        "session (CLI installed) | `alchemy-cli` |",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "| Run a one-off live query in this session (only MCP wired in) | `alchemy-mcp` |",
        "| Run a one-off live query, admin command, or on-machine automation in this "
        "session | `alchemy-mcp` |",
        1,
    ),
    remove_lines(
        f"{API}/SKILL.md",
        "| Build app code without an API key (autonomous agent, or explicit x402/MPP) | `agentic-gateway` |",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        "- Verify `$ALCHEMY_API_KEY` is set: `echo $ALCHEMY_API_KEY`",
        f"- Verify `$ALCHEMY_API_KEY` is set without printing it: {KEY_CHECK}",
        1,
    ),
    replace(
        f"{API}/SKILL.md",
        " (see `references/operational-allowlists.md`)",
        "",
        1,
    ),
    # =========================================================================
    # alchemy-api/references: "Other ways to access this API" (CLI, x402/MPP)
    # =========================================================================
]

for _path in OTHER_WAYS_FILES:
    OPERATIONS += [
        remove_list_item(_path, "**Live agent work via CLI**", 1),
        remove_list_item(_path, "**App code without an API key**", 1),
        replace(_path, " and the CLI is not installed", "", 1),
    ]

OPERATIONS += [
    # -- Cross-References: CLI, agentic-gateway and "when CLI is not installed" --
    remove_lines(f"{REF}/data-overview.md", "- `alchemy-cli` skill for live agent work", 1),
    remove_lines(f"{REF}/data-overview.md", "- `agentic-gateway` skill for app code without an API key", 1),
    replace(f"{REF}/data-overview.md", " (when CLI is not installed)", "", 1),
    remove_lines(f"{REF}/node-overview.md", "- `alchemy-cli` skill for live agent work", 1),
    remove_lines(f"{REF}/node-overview.md", "- `agentic-gateway` skill for app code without an API key", 1),
    replace(f"{REF}/node-overview.md", " (when CLI is not installed)", "", 1),
    remove_lines(f"{REF}/solana-overview.md", "- `alchemy-cli` skill for live agent work", 1),
    remove_lines(f"{REF}/solana-overview.md", "- `agentic-gateway` skill for app code without an API key", 1),
    replace(f"{REF}/solana-overview.md", " (when CLI is not installed)", "", 1),
    remove_lines(f"{REF}/solana-overview.md", "4. [solana-wallets.md](solana-wallets.md)", 1),
    remove_lines(f"{REF}/solana-overview.md", "- `wallets` skill → `wallets-solana-notes.md`", 1),
    replace(f"{REF}/solana-overview.md", SOLANA_WALLET_DESC_OLD, SOLANA_WALLET_DESC_NEW, 1),
    remove_lines(f"{REF}/solana-grpc-overview.md", "- `alchemy-cli` skill for live agent work", 1),
    replace(f"{REF}/solana-grpc-overview.md", " (when CLI is not installed)", "", 1),
    remove_lines(f"{REF}/sui-grpc-overview.md", "- `alchemy-cli` skill for live agent work", 1),
    replace(f"{REF}/sui-grpc-overview.md", " (when CLI is not installed)", "", 1),
    remove_lines(f"{REF}/sui-grpc-overview.md", "3. [sui-grpc-transactions.md](sui-grpc-transactions.md)", 1),
    replace(f"{REF}/sui-grpc-overview.md", "4. [sui-grpc-state-and-balances.md]", "3. [sui-grpc-state-and-balances.md]", 1),
    replace(f"{REF}/sui-grpc-overview.md", "5. [sui-grpc-move-packages.md]", "4. [sui-grpc-move-packages.md]", 1),
    replace(f"{REF}/sui-grpc-overview.md", "6. [sui-grpc-name-service.md]", "5. [sui-grpc-name-service.md]", 1),
    replace(f"{REF}/sui-grpc-overview.md", "7. [sui-grpc-subscriptions.md]", "6. [sui-grpc-subscriptions.md]", 1),
    replace(f"{REF}/sui-grpc-overview.md", "8. [sui-grpc-signature-verification.md]", "7. [sui-grpc-signature-verification.md]", 1),
    replace(
        f"{REF}/sui-grpc-overview.md",
        "querying and executing on Sui via Alchemy",
        "querying Sui via Alchemy",
        1,
    ),
    remove_lines(f"{REF}/sui-grpc-objects-and-ledger.md", "sui-grpc-transactions.md", 2),
    remove_lines(f"{REF}/webhooks-overview.md", "- `alchemy-cli` skill for live webhook management", 1),
    # -- Signing / broadcast content in retained files ---------------------------
    remove_section(f"{REF}/node-json-rpc.md", "## `eth_sendRawTransaction`"),
    replace(f"{REF}/node-json-rpc.md", ", `eth_sendRawTransaction`)", ")", 1),
    remove_lines(f"{REF}/solana-rpc.md", "  - solana-wallets.md", 1),
    remove_lines(f"{REF}/solana-rpc.md", "| `sendTransaction` | Submit a signed transaction |", 1),
    remove_lines(
        f"{REF}/solana-rpc.md",
        "- `simulateTransaction`, `sendTransaction`, and `getHealth` were briefly missing",
        1,
    ),
    remove_section(f"{REF}/solana-rpc.md", "## Jito bundles"),
    replace(
        f"{REF}/operational-supported-networks.md",
        "(`getblock`, `sendrawtransaction`, etc.)",
        "(`getblock`, etc.)",
        1,
    ),
    replace(
        f"{REF}/data-stellar-api.md",
        "for live ledger data, transaction submission, simulation, and Soroban contract calls",
        "for live ledger data, simulation, and Soroban contract calls",
        1,
    ),
    # -- Admin API: CLI references ------------------------------------------------
    replace(
        f"{REF}/operational-admin-api.md",
        "(browser-session-derived, or via the CLI's `alchemy auth login` path)",
        "(browser-session-derived)",
        1,
    ),
    replace(
        f"{REF}/operational-admin-api.md",
        "## When to use this vs the CLI",
        "## When to use this vs the MCP tools",
        1,
    ),
    replace(
        f"{REF}/operational-admin-api.md",
        "- Live agent work (browse apps, tweak allowlists, look up usage in a session) → "
        "use the `alchemy-cli` skill (`alchemy app *`, `alchemy usage *`). The CLI wraps "
        "this API cleanly and handles auth for you.",
        "- Live agent work (browse apps, tweak allowlists in a session) → use the "
        "`alchemy-mcp` skill (`list_apps`, `get_app`, `create_app`, `update_app`, "
        "`update_allowlist`). The MCP server wraps this API and handles auth for you.",
        1,
    ),
    replace(
        f"{REF}/operational-admin-api.md",
        "Re-run `alchemy auth login` or provide a fresh token.",
        "Provide a fresh token.",
        1,
    ),
    replace(
        f"{REF}/operational-admin-api.md",
        "- Verify the new key with `alchemy config get api-key` (via the CLI) or an "
        "authenticated dashboard reveal.",
        "- Verify the new key from the Alchemy Dashboard.",
        1,
    ),
    replace(
        f"{REF}/operational-admin-api.md",
        "this is a server / dashboard / CLI surface",
        "this is a server / dashboard surface",
        1,
    ),
    remove_list_item(f"{REF}/operational-admin-api.md", "**Live agent work via CLI**", 1),
    replace(
        f"{REF}/operational-admin-api.md",
        "(`alchemy-mcp` skill, when MCP is wired in but CLI isn't)",
        "(`alchemy-mcp` skill)",
        1,
    ),
    # -- Secrets: host-environment expansion in retained examples ----------------
    replace(
        f"{REF}/operational-auth-and-keys.md",
        'export ALCHEMY_API_KEY="..."\n'
        "curl -s https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY \\\n",
        "curl -s https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY \\\n",
        1,
    ),
    replace(
        f"{REF}/operational-jwt-and-header-auth.md",
        '-H "Authorization: Bearer $ALCHEMY_JWT"',
        '-H "Authorization: Bearer <ALCHEMY_JWT>"',
        1,
    ),
]

for _path, _count in FENCED_API_KEY_COUNTS.items():
    OPERATIONS.append(replace_in_fences(_path, "$ALCHEMY_API_KEY", "YOUR_API_KEY", _count))

OPERATIONS += [
    # -- skill-map.md --------------------------------------------------------------
    replace(
        SKILL_MAP,
        "> - **Live agent work** in this session: use `alchemy-cli` if `@alchemy/cli` is "
        "installed locally, otherwise `alchemy-mcp` (hosted MCP server).\n"
        "> - **App code without an API key** (autonomous agent, or explicit x402/MPP): use "
        "`agentic-gateway`.\n",
        "> - **Live agent work** in this session: use `alchemy-mcp` (hosted MCP server).\n"
        "> - **App code without an API key**: copy your API key from the Alchemy Dashboard "
        "(https://dashboard.alchemy.com) into `ALCHEMY_API_KEY`.\n",
        1,
    ),
    replace(SKILL_MAP, ", `eth_sendRawTransaction`)", ")", 1),
    replace(SKILL_MAP, SOLANA_WALLET_DESC_OLD, SOLANA_WALLET_DESC_NEW, 1),
    remove_lines(SKILL_MAP, "| `references/solana-wallets.md` |", 1),
    remove_lines(SKILL_MAP, "| `references/sui-grpc-transactions.md` |", 1),
    remove_section(SKILL_MAP, "## Wallets"),
]

for _name in MISSING_OPERATIONAL_ROWS:
    OPERATIONS.append(remove_lines(SKILL_MAP, f"| `references/{_name}` |", 1))

OPERATIONS += [
    remove_section(SKILL_MAP, "## Ecosystem"),
    # -- Dangling pointers to operational files that do not exist upstream -------
    remove_lines(f"{REF}/operational-auth-and-keys.md", "operational-allowlists.md", 2),
    remove_lines(f"{REF}/operational-best-practices.md", "operational-request-logs.md", 2),
    remove_lines(f"{REF}/operational-jwt-and-header-auth.md", "operational-allowlists.md", 2),
    replace(
        f"{REF}/operational-rate-limits-and-compute-units.md",
        "related:\n  - operational-pricing-and-plans.md\n  - data-apis\n",
        "related: []\n",
        1,
    ),
    remove_lines(f"{REF}/operational-rate-limits-and-compute-units.md", "- `operational-pricing-and-plans.md`", 1),
    replace(
        f"{REF}/rollups-details.md",
        "related:\n  - operational-pricing-and-plans.md\n",
        "related: []\n",
        1,
    ),
    remove_section(f"{REF}/rollups-details.md", "## Related Files"),
]

# ---------------------------------------------------------------------------
# Forbidden-content scan
# ---------------------------------------------------------------------------

FAIL_PATTERNS = [
    r"agentic-gateway",
    r"x402",
    r"mpp\.alchemy\.com",
    r"\bMPP\b",
    r"\balchemy-cli\b",
    r"npm i(nstall)? -g @alchemy/cli",
    r"\bnpx\b",
    r"--reveal",
    r"echo\s+\$ALCHEMY_API_KEY",
    r"\balchemy\s+(evm\s+send|solana\s+send|evm\s+contract\s+call|evm\s+approve"
    r"|evm\s+swap\s+execute|xchain\s+bridge\s+execute|x402\s+request|wallet\s+connect)\b",
    r"\b(eth_)?sendRawTransaction\b",
    r"\bsendrawtransaction\b",
    r"\b\w*_?sendTransaction\b",
    r"\bsendBundle\b",
    r"\bsendCalls\b",
    r"\bsendPreparedCalls\b",
    r"\bsendUserOperation\b",
    r"\bExecuteTransaction\b",
    r"executeTransactionBlock",
    r"\b(eth_sign|personal_sign|signTypedData\w*|signTransaction|signMessage|signAuthorization)\b",
    r"--wallet-key-file",
    r"ALCHEMY_WALLET_KEY",
    r"--gas-sponsored",
    r"--fee-sponsored",
    # Namespace variants
    r"\beth_sendUserOperation\b",
    r"\bwallet_sendPreparedCalls\b",
    r"\bwallet_sendCalls\b",
    r"\beth_signTypedData(_v\d)?\b",
    r"\beth_signTransaction\b",
]

REVIEW_PATTERNS = [
    r"private key",
    r"\bsign",
    r"transfer",
    r"paymaster",
    r"faucet",
    r"airdrop",
    r"wallet",
    r"API key",
]

# Exact (file, snippet, expected_line_count, reason) entries for FAIL hits that
# review approved as false positives. Never whole-file exemptions.
ALLOW = []


def scan(texts):
    fail_res = [(p, re.compile(p, re.I)) for p in FAIL_PATTERNS]
    review_res = [(p, re.compile(p, re.I)) for p in REVIEW_PATTERNS]
    failures = []
    review = []
    for path in sorted(texts):
        for number, line in enumerate(texts[path].split("\n"), 1):
            for pattern, regex in fail_res:
                if regex.search(line):
                    failures.append((path, number, pattern, line))
            for pattern, regex in review_res:
                if regex.search(line):
                    review.append((path, number, pattern, line))
    errors = []
    allowed = set()
    for entry in ALLOW:
        path, snippet, expected = entry[0], entry[1], entry[2]
        lines = {(p, n) for p, n, _, text in failures if p == path and snippet in text}
        if len(lines) != expected:
            errors.append(
                f"{path}: allow entry {snippet!r} expected {expected} line(s), "
                f"found {len(lines)} (upstream changed: update the override)"
            )
        allowed |= lines
    remaining = [f for f in failures if (f[0], f[1]) not in allowed]
    return remaining, review, errors


# ---------------------------------------------------------------------------
# Reference check
# ---------------------------------------------------------------------------

LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
TICK_RE = re.compile(r"`([^`\s]+\.md)`")


def slugify(heading):
    text = heading.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def split_frontmatter(lines):
    if not lines or lines[0] != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index] == "---":
            return index
    return None


def resolve(files, source, ref):
    ref = ref.split("#")[0]
    if ref.startswith("references/"):
        target = os.path.normpath(os.path.join(source.split("/")[0], ref))
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(source), ref))
    return target.replace(os.sep, "/") in files


def check_references(files):
    problems = []
    for path in sorted(files):
        if not path.endswith(".md"):
            continue
        lines = files[path].split("\n")
        info = scan_fences(lines)
        end = split_frontmatter(lines)
        anchors = set()
        for number, line in enumerate(lines, 1):
            heading = HEADING_RE.match(line)
            if heading and not info[number - 1][0] and (end is None or number > end + 1):
                anchors.add(slugify(line.lstrip("#")))
        for number, line in enumerate(lines, 1):
            for match in LINK_RE.finditer(line):
                target = match.group(1)
                if "://" in target or target.startswith("mailto:"):
                    continue
                if target.startswith("#"):
                    if target[1:] not in anchors:
                        problems.append(f"{path}:{number}: broken anchor link {target}")
                elif target.split("#")[0].endswith(".md") and not resolve(files, path, target):
                    problems.append(f"{path}:{number}: broken link {target}")
            for match in TICK_RE.finditer(line):
                target = match.group(1)
                if "://" not in target and not resolve(files, path, target):
                    problems.append(f"{path}:{number}: broken path `{target}`")
        if end is not None:
            in_related = False
            for number in range(2, end + 1):
                line = lines[number - 1]
                if line.startswith("related:"):
                    in_related = line.strip() == "related:"
                    if not in_related and line.strip() != "related: []":
                        problems.append(f"{path}:{number}: unsupported related: form")
                    continue
                if in_related:
                    entry = re.match(r"^\s+-\s+(\S+)\s*$", line)
                    if entry:
                        value = entry.group(1).strip("'\"")
                        if not resolve(files, path, value):
                            problems.append(f"{path}:{number}: broken related entry {value}")
                    else:
                        in_related = False
    return problems


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def scan_fences(lines):
    """Per line: (inside_fence, fence_language, is_fence_delimiter)."""
    info = []
    fence = None
    for line in lines:
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                rest = match.group(2).strip()
                fence = (match.group(1)[0], len(match.group(1)), rest.split()[0] if rest else "")
                info.append((True, fence[2], True))
            else:
                info.append((False, None, False))
        elif (
            match
            and match.group(1)[0] == fence[0]
            and len(match.group(1)) >= fence[1]
            and not match.group(2).strip()
        ):
            info.append((True, fence[2], True))
            fence = None
        else:
            info.append((True, fence[2], False))
    return info


def indent_of(line):
    return len(line) - len(line.lstrip(" "))


def delete_ranges(lines, ranges):
    for start, end in sorted(ranges, reverse=True):
        del lines[start:end]
        while 0 < start < len(lines) and lines[start].strip() == "" and lines[start - 1].strip() == "":
            del lines[start]


def item_end(lines, start):
    marker = LIST_ITEM_RE.match(lines[start])
    base = len(marker.group(1))
    fence = None
    index = start + 1
    while index < len(lines):
        line = lines[index]
        if fence is not None:
            match = FENCE_RE.match(line)
            if (
                match
                and match.group(1)[0] == fence[0]
                and len(match.group(1)) >= fence[1]
                and not match.group(2).strip()
            ):
                fence = None
            index += 1
            continue
        if line.strip() == "":
            probe = index
            while probe < len(lines) and lines[probe].strip() == "":
                probe += 1
            if probe < len(lines) and indent_of(lines[probe]) > base:
                index = probe
                continue
            break
        if indent_of(line) > base:
            match = FENCE_RE.match(line)
            if match:
                fence = (match.group(1)[0], len(match.group(1)))
            index += 1
            continue
        break
    return index


# ---------------------------------------------------------------------------
# Operation execution
# ---------------------------------------------------------------------------


class Tree:
    def __init__(self, root):
        self.root = root
        self.files = {}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            for name in sorted(filenames):
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                if os.path.islink(full):
                    raise OverrideError(f"{rel}: symlink in input")
                with open(full, "rb") as handle:
                    data = handle.read()
                try:
                    self.files[rel] = data.decode("utf-8")
                except UnicodeDecodeError:
                    raise OverrideError(f"{rel}: not valid UTF-8")
        self.original = dict(self.files)

    def text(self, path):
        if path not in self.files:
            raise OverrideError(f"{path}: file not found (upstream changed: update the override)")
        return self.files[path]


def mismatch(path, what, expected, found):
    raise OverrideError(
        f"{path}: {what}: expected {expected} match(es), found {found} "
        "(upstream changed: update the override)"
    )


def do_remove_file(tree, o):
    tree.text(o["path"])
    del tree.files[o["path"]]
    return 1


def do_remove_glob(tree, o):
    matches = sorted(p for p in tree.files if fnmatch.fnmatchcase(p, o["path"]))
    if len(matches) != o["args"]["count"]:
        mismatch(o["path"], "remove_glob", o["args"]["count"], len(matches))
    for path in matches:
        del tree.files[path]
    return len(matches)


def do_remove_section(tree, o):
    path, heading = o["path"], o["args"]["heading"]
    level_match = HEADING_RE.match(heading)
    if not level_match:
        raise OverrideError(f"{path}: remove_section anchor {heading!r} is not a heading line")
    level = len(level_match.group(1))
    lines = tree.text(path).split("\n")
    info = scan_fences(lines)
    starts = [i for i, line in enumerate(lines) if line == heading and not info[i][0]]
    if len(starts) != 1:
        mismatch(path, f"remove_section {heading!r}", 1, len(starts))
    start = starts[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = HEADING_RE.match(lines[index])
        if match and not info[index][0] and len(match.group(1)) <= level:
            end = index
            break
    if end == len(lines) and lines[-1] == "":
        end -= 1
    del lines[start:end]
    while len(lines) >= 2 and lines[-1] == "" and lines[-2] == "":
        lines.pop()
    tree.files[path] = "\n".join(lines)
    return 1


def do_remove_lines(tree, o):
    path, snippet, count = o["path"], o["args"]["snippet"], o["args"]["count"]
    lines = tree.text(path).split("\n")
    hits = [i for i, line in enumerate(lines) if snippet in line]
    if len(hits) != count:
        mismatch(path, f"remove_lines {snippet!r}", count, len(hits))
    delete_ranges(lines, [(i, i + 1) for i in hits])
    tree.files[path] = "\n".join(lines)
    return count


def do_remove_list_item(tree, o):
    path, snippet, count = o["path"], o["args"]["snippet"], o["args"]["count"]
    lines = tree.text(path).split("\n")
    hits = [i for i, line in enumerate(lines) if snippet in line]
    if len(hits) != count:
        mismatch(path, f"remove_list_item {snippet!r}", count, len(hits))
    ranges = []
    for index in hits:
        if not LIST_ITEM_RE.match(lines[index]):
            raise OverrideError(f"{path}:{index + 1}: remove_list_item {snippet!r} is not a list item line")
        ranges.append((index, item_end(lines, index)))
    delete_ranges(lines, ranges)
    tree.files[path] = "\n".join(lines)
    return count


def do_replace(tree, o):
    path, old, new, count = o["path"], o["args"]["old"], o["args"]["new"], o["args"]["count"]
    text = tree.text(path)
    found = text.count(old)
    if found != count:
        mismatch(path, f"replace {old[:60]!r}", count, found)
    tree.files[path] = text.replace(old, new)
    return count


def do_replace_in_fences(tree, o):
    path, old, new, count = o["path"], o["args"]["old"], o["args"]["new"], o["args"]["count"]
    langs = o["args"]["langs"]
    lines = tree.text(path).split("\n")
    info = scan_fences(lines)
    found = 0
    for index, line in enumerate(lines):
        inside, lang, delimiter = info[index]
        if inside and not delimiter and lang in langs and old in line:
            found += line.count(old)
            lines[index] = line.replace(old, new)
    if found != count:
        mismatch(path, f"replace_in_fences {old!r}", count, found)
    tree.files[path] = "\n".join(lines)
    return count


def do_set_frontmatter_scalar(tree, o):
    path, key, new_value = o["path"], o["args"]["key"], o["args"]["value"]
    lines = tree.text(path).split("\n")
    end = split_frontmatter(lines)
    if end is None:
        raise OverrideError(f"{path}: no YAML frontmatter")
    hits = [i for i in range(1, end) if lines[i].startswith(f"{key}:")]
    if len(hits) != 1:
        mismatch(path, f"frontmatter {key}:", 1, len(hits))
    index = hits[0]
    current = lines[index][len(key) + 1:].strip()
    following = lines[index + 1] if index + 1 < len(lines) else ""
    if not current or current[0] in "'\">|" or following[:1] in (" ", "\t"):
        raise OverrideError(f"{path}: frontmatter {key} must be a single-line plain scalar")
    if ": " in new_value or " #" in new_value or new_value[0] in "-?:,[]{}#&*!|>'\"%@`":
        raise OverrideError(f"{path}: new {key} is not a safe YAML plain scalar")
    lines[index] = f"{key}: {new_value}"
    tree.files[path] = "\n".join(lines)
    return 1


HANDLERS = {
    "remove_file": do_remove_file,
    "remove_glob": do_remove_glob,
    "remove_section": do_remove_section,
    "remove_lines": do_remove_lines,
    "remove_list_item": do_remove_list_item,
    "replace": do_replace,
    "replace_in_fences": do_replace_in_fences,
    "set_frontmatter_scalar": do_set_frontmatter_scalar,
}


def describe(o):
    args = o["args"]
    detail = args.get("heading") or args.get("snippet") or args.get("old") or args.get("key") or ""
    detail = detail.replace("\n", "\\n")
    if len(detail) > 70:
        detail = detail[:67] + "..."
    count = args.get("count")
    suffix = f" x{count}" if count is not None else ""
    return f"{o['kind']} {detail}{suffix}".rstrip()


def read_commands(commands_dir):
    texts = {}
    if not commands_dir or not os.path.isdir(commands_dir):
        return texts
    for dirpath, dirnames, filenames in os.walk(commands_dir):
        dirnames.sort()
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            rel = "commands/" + os.path.relpath(full, commands_dir).replace(os.sep, "/")
            with open(full, "r", encoding="utf-8") as handle:
                texts[rel] = handle.read()
    return texts


def write_tree(tree):
    for rel in sorted(set(tree.original) - set(tree.files)):
        os.remove(os.path.join(tree.root, rel))
    for rel in sorted(tree.files):
        if tree.original.get(rel) != tree.files[rel]:
            with open(os.path.join(tree.root, rel), "wb") as handle:
                handle.write(tree.files[rel].encode("utf-8"))
    for dirpath, dirnames, filenames in os.walk(tree.root, topdown=False):
        if dirpath != tree.root and not os.listdir(dirpath):
            os.rmdir(dirpath)
    with open(os.path.join(tree.root, MARKER), "w", encoding="utf-8") as handle:
        handle.write(MARKER_TEXT)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("skills_dir")
    parser.add_argument(
        "--commands",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins", "alchemy", "commands"),
        help="slash commands directory to include in the forbidden-content scan",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="print every operation and every REVIEW hit"
    )
    args = parser.parse_args(argv)

    root = args.skills_dir
    if not os.path.isdir(root):
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 1
    if os.path.exists(os.path.join(root, MARKER)):
        print(
            f"error: {root} already contains {MARKER}; the overrides were already applied. "
            "Re-run scripts/sync-skills.sh to regenerate it from the pinned source.",
            file=sys.stderr,
        )
        return 1

    try:
        tree = Tree(root)
        per_file = {}
        for index, operation in enumerate(OPERATIONS, 1):
            handled = HANDLERS[operation["kind"]](tree, operation)
            per_file[operation["path"]] = per_file.get(operation["path"], 0) + 1
            if args.verbose:
                print(f"  [{index:03d}] {operation['path']}: {describe(operation)} -> {handled}")
    except OverrideError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"Applied {len(OPERATIONS)} operations across {len(per_file)} paths.")

    scanned = dict(tree.files)
    scanned.update(read_commands(args.commands))
    failures, review, allow_errors = scan(scanned)
    problems = check_references(tree.files)

    for error in allow_errors:
        print(f"error: {error}", file=sys.stderr)
    for path, number, pattern, line in failures:
        print(f"FAIL {path}:{number} [{pattern}] {line.strip()[:160]}", file=sys.stderr)
    for problem in problems:
        print(f"BROKEN {problem}", file=sys.stderr)

    counts = {pattern: 0 for pattern in REVIEW_PATTERNS}
    for _, _, pattern, _ in review:
        counts[pattern] += 1
    print(
        "REVIEW hits per pattern (not failed; --verbose lists every hit): "
        + ", ".join(f"{pattern} {count}" for pattern, count in counts.items())
    )
    if args.verbose:
        for path, number, pattern, line in review:
            print(f"REVIEW {path}:{number} [{pattern}] {line.strip()[:140]}")
    print(
        f"Scan: {len(failures)} FAIL, {len(review)} REVIEW, {len(problems)} broken references, "
        f"{len(ALLOW)} allow entries."
    )
    if failures or problems or allow_errors:
        return 1

    write_tree(tree)
    print(f"Wrote {len(tree.files)} files plus {MARKER}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
