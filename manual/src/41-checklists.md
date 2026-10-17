## The checklists {#ch-checklists}

::: {.dek}
Five lists, for five moments. Each item points to the chapter that explains it.
:::

### Before you start a project

::: {.box .do-this}
**Before you start**

- Create a `.gitignore` that includes `.env` and `.env.*`, and a `.env.example` with fake values ({{ch:ch-secrets}}).
- Install a secret scanner that runs before every commit and push ({{ch:ch-kit}}).
- Add your agent's rules file and guard hook ({{ch:ch-agent-rules}}; {{ch:ch-kit}}).
- Create separate development and production databases and keys ({{ch:ch-least-privilege}}).
- Use a package manager setting that waits before installing brand-new versions, and blocks unreviewed install scripts ({{ch:ch-dependencies}}).
- Turn on passkeys or MFA for GitHub, your host, your database and your payment provider ({{ch:ch-accounts}}).
:::

### Before every push

::: {.box .do-this}
**Before every push**

- Read the list of changed files. Stop at any key, new package, settings file or workflow change you did not ask for ({{ch:ch-agent}}).
- Let the secret scanner run. Never skip it with `--no-verify` ({{ch:ch-secrets}}).
- Check that no secret has a public prefix (`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`, `PUBLIC_`) ({{ch:ch-secrets}}).
- Run the tests yourself. Do not rely on the agent's report ({{ch:ch-agent}}).
:::

### Before you launch

::: {.box .do-this}
**Before you launch**

- Every table has row-level security or security rules, with owner-only policies ({{ch:ch-doors}}).
- You ran the stranger test and the second-user test, and both passed ({{ch:ch-doors}}).
- Payment status and permissions are checked on the server, and webhooks verify signatures ({{ch:ch-doors}}).
- Production keys live in the host's secret settings, marked secret, and nowhere else ({{ch:ch-secrets}}).
- Every paid service has a hard cap where one exists, and low alerts where it does not ({{ch:ch-money}}).
- HTTPS everywhere, with security headers, checked with the HTTP Observatory ({{ch:ch-websites}}).
- No dashboard or admin page is reachable from the internet ({{ch:ch-connection}}).
- A backup exists off-site, with a key that cannot delete, and you have restored from it ({{ch:ch-backups}}).
- You have a leak card: every key and the page where it is revoked ({{ch:ch-leak}}).
:::

### Every month

::: {.box .do-this}
**Every month**

- Review connected apps on Google and GitHub, and remove what you do not use ({{ch:ch-accounts}}).
- Look at every bill. Investigate any unexpected rise ({{ch:ch-money}}).
- Restore a few random files from your backup and compare them ({{ch:ch-backups}}).
- Update your framework, your packages and your AI tools. Read the security notices ({{ch:ch-dependencies}}; {{ch:ch-react2shell}}).
- Check that nothing new is exposed: open ports, dashboards, test pages ({{ch:ch-connection}}).
- Run the kit's doctor in each project ({{ch:ch-kit}}).
:::

### When something leaks

::: {.box .do-this}
**When something leaks**

- Revoke or rotate the key at the provider, now ({{ch:ch-leak}}).
- Create a smaller replacement, store it as a secret, redeploy and test ({{ch:ch-leak}}).
- Check logs and bills for the time the key was exposed ({{ch:ch-leak}}).
- Only then clean the code and its history ({{ch:ch-leak}}).
- After a poisoned package or a framework flaw, rotate every key the affected machine could reach ({{ch:ch-leak}}).
- Write down what happened, and what you changed so it cannot happen again.
:::
