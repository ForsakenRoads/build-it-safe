---
name: secure-build
description: Security protocol for building software with an AI agent. Use it whenever the work touches API keys, secrets, tokens, passwords or .env files; login, sign-up, sessions or user permissions; payments, Stripe, webhooks or billing; databases, Supabase, Firebase, SQL, migrations or Row Level Security; deploys, hosting, Vercel, Netlify, Cloudflare, domains or CI workflows; installing a new package, dependency, MCP server, plugin or skill; backups and restores; or a suspected leak, breach or incident.
metadata:
  kit: build-it-safe
  version: "1"
---

# Secure build protocol

This skill holds the full protocol behind the short security rules in AGENTS.md or CLAUDE.md. Those rules still apply here. A guard hook blocks the worst actions (reading secret files, destructive commands, `curl | sh`, skipped checks, literal keys in files). If the guard blocks you, do not look for another way to do the same thing: tell the human what you were trying to do and why.

## First, find the part that matches the task

| The task touches | Read |
|---|---|
| API keys, tokens, `.env`, environment variables, front-end config | [references/secrets.md](references/secrets.md) |
| Login, sign-up, sessions, roles, Supabase or Firebase rules, user data | [references/auth-and-data.md](references/auth-and-data.md) |
| Payments, Stripe, webhooks | [references/auth-and-data.md](references/auth-and-data.md) (webhooks) and [references/secrets.md](references/secrets.md) (keys) |
| Installing or upgrading a package, a lockfile, install scripts | [references/dependencies.md](references/dependencies.md) |
| Deploys, hosting, domains, CI workflows, spending limits | [references/deploys.md](references/deploys.md) |
| MCP servers, plugins, skills, other agents, agent settings | [references/agents-and-tools.md](references/agents-and-tools.md) |
| Backups, restores, deleting data | [references/backups.md](references/backups.md) |
| A key that may have leaked, a breach, strange charges | [references/incidents.md](references/incidents.md), at once |

Read only the page you need. Each page ends with a checklist.

## The protocol in brief

1. **Secrets stay out of reach.** Never open `.env` or key files. Code reads `process.env.NAME` (or the language's equivalent). New variables go into `.env.example` with a placeholder value, and the human puts the real value in `.env` or the host's secret store.
2. **The browser is public.** Anything sent to the browser, including every `NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`, `PUBLIC_` or `REACT_APP_` variable, can be read by anyone. Server-only keys stay on the server.
3. **Check access on the server, every time.** Hiding a button is not access control. Every route and table checks who the user is and what they may see.
4. **Least privilege.** Use the narrowest key that works: restricted Stripe keys, publishable Supabase keys in the browser, scoped tokens with an expiry date.
5. **Every package runs code.** Confirm a package exists and is the one intended before adding it. Keep the lockfile committed.
6. **No production from the agent.** Development and production are separate. The agent never holds production keys or runs commands against production data.
7. **Backups are tested.** A backup counts only after a restore from it has worked.
8. **When something leaks, revoke first.** Revoke or rotate at the provider, then clean up the code and history.

## When you finish

Before you say the task is done:
- run `git diff` and look for keys, tokens, `.env` content, disabled checks and new dependencies;
- say which security-relevant changes you made (auth, data access, keys, packages, CI);
- say what you could not check, such as Row Level Security policies in a dashboard, so the human can check it.

The human reviews every change before it is merged. Your summary helps them do that.
