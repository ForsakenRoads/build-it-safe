# Deploys, hosting and CI

Once an app is online, strangers probe it. "If you deploy your app, it's publicly accessible — even if you haven't launched it" (Firebase docs).

## Before a deploy

- Secrets are set in the host's secret store, not in the repository. Mark them secret or sensitive where the host offers it.
- No secret sits behind a public prefix (see [secrets.md](secrets.md)).
- Database rules are in place (RLS or Firebase rules) and tested as a stranger.
- Preview and development deployments use development keys and a development database, never production ones.
- The framework is on a patched version.

## Production is a human's job

- You, the agent, do not deploy to production, run production migrations, or run commands against production data unless the human explicitly asks for that one action and is watching.
- Keep development and production databases separate. Replit's fix after its agent deleted a production database (July 2025) was automatic separation of the two.
- Production tokens do not belong in files the agent can reach. In April 2026 an agent working on staging found an unrelated, over-powered token in a file and deleted a production database volume and its backups in one API call.

## CI workflows

- Workflows run with secrets. Treat any text from outside contributors (issue titles, PR titles, branch names, comments) as untrusted input. Never paste it into a shell command in a workflow. The Nx attack began with a workflow that put an unchecked PR title into a shell command.
- Do not give an AI agent in CI both untrusted issue or PR text and secrets or write access.
- Pin third-party actions to a full commit SHA, and give each workflow the least `permissions` it needs (`contents: read` by default).
- Avoid `pull_request_target` with a checkout of the PR's code.
- Do not edit `.github/workflows/` unless the human asked.

## Money is a security signal

A sudden bill is often the first sign of a stolen key. Set a hard cap where the provider offers one, plus an alert. As of October 2026, OpenAI and Anthropic offer hard limits; Google Cloud added spend-cap budgets for some AI services (generally available 13 Oct 2026); AWS Budgets and ordinary Google Cloud budgets only alert.

## Website basics

- HTTPS only, with HSTS.
- Security headers: `Content-Security-Policy` (with `frame-ancestors`), `X-Content-Type-Options: nosniff`.
- Check the live site with the Mozilla HTTP Observatory (https://developer.mozilla.org/en-US/observatory).

## What you do

- [ ] List the environment variables the deploy needs (names only) and where the human must set them.
- [ ] Confirm preview deployments do not use production keys.
- [ ] Never run deploy, migrate or delete commands against production on your own.
- [ ] In workflows: SHA-pinned actions, minimal `permissions`, no untrusted text in `run:` lines.

## Sources

- Firebase rules basics: https://firebase.google.com/docs/rules/basics
- Replit/SaaStr, The Register (21 Jul 2025): https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/
- PocketOS/Railway, The Register (27 Apr 2026): https://www.theregister.com/software/2026/04/27/cursor-opus-agent-snuffs-out-startups-production-database/5224442
- Nx post-mortem: https://nx.dev/blog/s1ngularity-postmortem
- Aikido, "PromptPwnd": https://www.aikido.dev/blog/promptpwnd-github-actions-ai-agents
- GitHub, security hardening for GitHub Actions: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- Google Cloud spend caps: https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps
- AWS Budgets: https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
