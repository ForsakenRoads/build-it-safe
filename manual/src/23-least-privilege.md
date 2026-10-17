## Least privilege {#ch-least-privilege}

::: {.dek}
Give every key the smallest power that still does the job.
:::

### The mental model: the valet key

Some cars come with a valet key. It starts the engine, but it does not open the trunk or the glove box. You hand it to a stranger without worrying, because the worst they can do is small.

**Least privilege** means giving every key, account and tool the smallest power that still does its job. Then, when a key leaks, and over the years one will, the damage is small. AWS puts it in one line: "Grant only the permissions required to perform a task" [[aws-iam-best]].

![A master key opens everything. Scoped keys each open one thing, so one leak stays small.](images/diagrams/scoped-keys.svg){width=90%}

### A story about one token

In April 2026 a coding agent working for a small company called PocketOS hit an error while working on a *staging* system, a test copy. It found an access token for the hosting company Railway in an unrelated file and used it. In one request, it deleted the *production* database volume, and with it the backups, which were stored in the same volume [[register-pocketos]]. The token had been created to add and remove web domains, but it was "scoped for any operation, including destructive ones". The founder said the deletion took "9 seconds" [[register-pocketos]]. Railway restored the data, and from 1 May 2026 made volume deletions through its API undoable for 48 hours [[railway-undoable-deletes]].

The agent made a bad decision. But a token that could only manage domains would have turned that bad decision into an error message.

### Scoped keys, provider by provider

Most services now let you make keys with limited power. As of October 2026:

- **Stripe** offers publishable keys (`pk_`), secret keys (`sk_`) with full power, and **restricted keys** (`rk_`) whose permissions you choose. Stripe now writes: "we don't recommend using secret keys for new use cases" and recommends migrating to restricted keys [[stripe-keys]]. Restricted keys can also be marked for use by AI agents, which puts payouts and refunds behind approval rules [[stripe-keys]].
- **Supabase** separates the **publishable** key (`sb_publishable_…`), safe in browsers when RLS is on, from the **secret** key (`sb_secret_…`), which bypasses RLS and belongs only on servers [[supabase-api-keys]].
- **Anthropic** lets you create **workspaces** inside your account. Each workspace can have its own API keys and its own spending limit [[anthropic-workspaces]]. Use one workspace per app or per environment.
- **GitHub** recommends "fine-grained personal access tokens instead of personal access tokens (classic) whenever possible". A fine-grained token can be limited to one repository and given an expiry date [[github-pat]].
- **AWS** recommends temporary credentials and roles over long-lived access keys [[aws-iam-best]].
- **Backblaze B2** application keys can be limited to one bucket and to chosen actions, such as "write but never delete" ({{ch:ch-backups}}).

### Development versus production

Keep two worlds apart:

- **Development** is where you and your AI agent build and break things. It has its own database, filled with fake data, and its own keys with low limits.
- **Production** is the live app with real users. Its keys live only in your host's secret settings. You change it on purpose, through a deploy, not from your laptop.

Replit's fix after the SaaStr incident was exactly this: automatic separation between development and production databases ({{ch:ch-replit}}). If your tools do not separate them for you, do it yourself: two databases, two sets of keys, and no production keys on the computer where your agent works.

### Common AI-assistant mistakes

- Using the most powerful key available because "it works", such as Stripe's full secret key or Supabase's secret key, when a restricted or publishable key would do.
- Creating a GitHub or cloud token with every permission ticked.
- Pointing the app on your laptop at the production database "to test with real data".
- Reusing one key across several apps, so one leak breaks all of them.

::: {.box .ask-agent}
**Ask your agent**

"List every key and token this project uses. For each, tell me what it can do, and suggest the narrowest kind of key the provider offers for what we actually need. Do not print any values."
:::

::: {.box .do-this}
**Do this**

- Replace full-power keys with restricted or scoped keys wherever the provider offers them.
- Give every token an expiry date where you can.
- Use one key per app and per environment, never one key everywhere.
- Keep a separate development database and development keys. Keep production keys off the machine where your agent works.
:::
