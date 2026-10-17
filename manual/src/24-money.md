## Money is a security signal {#ch-money}

::: {.dek}
An alert tells you about the fire. A cap stops it.
:::

### The mental model: alerts versus caps

When a key leaks, the first sign is often not a security warning. It is a bill. EnrichLead's founder noticed "maxed out usage on api keys" ({{ch:ch-enrichlead}}). Sysdig estimated that stolen cloud credentials, used to run AI models, "could result in over $46,000 of LLM consumption costs per day" ({{ch:ch-published-keys}}). So your spending settings are security settings.

There are two kinds, and they are easy to confuse:

- An **alert** sends you an email when spending passes an amount. The spending continues. If the alert arrives at 3 a.m., the bill keeps growing until you wake up.
- A **hard cap** stops the service when spending reaches an amount. Your app may stop working, but the bill stops too.

Many providers offer only alerts, or offer caps that act a few minutes late. Know which one you have.

### Provider by provider, as of October 2026

Prices and features change often. Check each provider's page before you rely on this table.

| Provider | What you can set | Hard cap? |
|----|------------|---|
| OpenAI API | "Spend alerts": "Sends a notification; API traffic continues." A separate "Enforce a hard limit" switch for an organization or a project. "Enforcement is not instantaneous" [[openai-spend-limits]] | Yes, with a small overrun possible |
| Anthropic API | A monthly cap for each usage tier, a lower limit you choose on the Billing page, and a spend limit per workspace [[anthropic-rate-limits; anthropic-workspaces]] | Yes |
| Google Cloud (general) | Budgets. "Setting an alerts-only budget doesn't automatically cap … usage or spending" [[gcp-budgets]] | No |
| Google Cloud spend caps (Gemini API, Gemini Enterprise Agent Platform, formerly Vertex AI, Cloud Run and Cloud Run functions) | Generally available since 13 October 2026. New requests pause when the cap triggers; "enforcement of spend caps isn't instant and any cost overages are billed as normal" [[gcp-spend-caps; gcp-billing-notes]] | Nearly |
| Gemini API (AI Studio) | Project spend caps, which Google's billing documentation calls experimental, with "a ~10 minute delay", and "users are responsible for overages incurred during that period"; plus a monthly cap for each billing tier [[google-gemini-costs; gemini-billing]] | Nearly |
| AWS | Budgets alert on cost. "Budget actions" can block new resources. "You might incur additional costs … before AWS Budgets can notify you" [[aws-budgets]] | No |
| Vercel (Pro and Enterprise) | Spend Management. "Setting a spend amount does not stop usage on its own": turn on "Pause Production Deployments" to stop it. Checks run every few minutes [[vercel-spend]] | With pausing on, nearly |
| Supabase (Pro) | A Spend Cap: past your plan's quota, "further usage of that item is disallowed until the next billing cycle" for the items it covers [[supabase-cost-control]] | Yes, for covered items |

A few notes on the table:

- **Vercel's pause has gaps.** It pauses your production sites. It "does not stop AI Gateway API key usage or v0 usage billed to your team", and storage keeps being billed [[vercel-spend]].
- **AWS has a safer starting point for new accounts.** When you sign up, you can choose a Free account plan. AWS says: "You will not incur any charges during this period until you upgrade to a paid account plan." It lasts up to six months, or until the credits are used [[aws-free-plan]].
- **"Nearly" still matters.** A cap that acts ten minutes late stops a $46,000-a-day attack at about $320 (ten minutes is 1/144 of a day). An alert that you read the next morning does not. But a late cap limits the damage; it does not prevent it. The alert is the signal you must act on: when it arrives, find out why, and revoke the key if you cannot explain the spending.

### Set the cap low, then raise it

Start with a cap a little above what your app really uses. If your app hits the cap, you will find out quickly, and you can raise it. If someone steals your key, the cap limits the damage to an amount you chose in advance.

Set an alert at a lower level too, such as half the cap. The alert is your early warning; the cap is your guarantee.

### Common AI-assistant mistakes

- Telling you that a budget "will stop charges" when it only sends emails.
- Using one key for every environment, so a runaway test loop in development spends production money.
- Writing code that retries failed AI calls in a tight loop, which can multiply a bill in minutes.

::: {.box .watch-out}
**Watch out**

A budget is not a cap. Before you trust any spending setting, find the sentence in the provider's documentation that says what happens when the amount is reached. If it says "notification", "alert" or "email", the spending continues.
:::

::: {.box .do-this}
**Do this**

- For every paid service, write down whether it offers a hard cap, and set one if it does.
- Where only alerts exist, set them low, and send them to a channel you read quickly.
- Use separate keys, with separate limits, for development and production.
- Look at every bill when it arrives. An unexpected rise is a security alarm until proven otherwise.
:::
