---
description: Connect and select an Alchemy app for this session
argument-hint: "[app name or id]"
---

Set up Alchemy for this session so other tools have an API key to use:

1. Call the `list_apps` tool to fetch the user's Alchemy apps.
2. Pick the app:
   - If the user named one in "$ARGUMENTS", match it.
   - Else if exactly one app exists, select it automatically.
   - Else show the list (id + name) and ask which one to use. Do NOT guess when multiple exist.
3. Call `select_app` with the chosen app id to cache its API key for the rest of the session.

Confirm which app is now selected. If the call fails with an auth error, tell the user to connect/authenticate the Alchemy connector first (OAuth via the Alchemy Dashboard).
