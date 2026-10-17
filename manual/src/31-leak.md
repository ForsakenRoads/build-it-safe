## When something leaks {#ch-leak}

::: {.dek}
Revoke first. Clean up second. Learn third.
:::

### The mental model: the clock started before you noticed

When a key leaks, you are racing programs, not people. Clutch Security's planted keys were used after 6.6 minutes on average ({{ch:ch-published-keys}}). By the time you notice, someone may already have the key. So the first move is never "delete the file" or "hide the commit". It is to make the key worthless: **revoke** it at the provider, so it stops working everywhere, including in every copy you cannot see. GitHub's guide to removing secrets says the same: "As a first step you need to revoke and/or rotate that secret" [[github-remove-sensitive]].

![The order matters. Revoking takes a minute and protects you everywhere; cleaning history takes hours and cannot reach copies that already exist.](images/diagrams/leak-playbook.svg){width=95%}

::: {.box .plain-words}
**Plain words**

- **Revoke:** cancel a key at the service that issued it, so it no longer works.
- **Rotate:** replace a key with a new one, then revoke the old one.
:::

### The playbook

**1. Revoke or rotate the key at the provider, now.** Open the provider's dashboard (Stripe, OpenAI, Supabase, AWS, GitHub and so on), find the key, and revoke it or roll it. For a planned rotation, Stripe lets the old and new keys both work for up to 7 days while you switch over [[stripe-keys]]. For a leak, give no grace period.

**2. Make the replacement smaller than the original.** Create the new key with the least power that works ({{ch:ch-least-privilege}}).

**3. Store it in the right place.** Put the new key in your host's secret settings, marked secret, and in your local `.env`. Not in code, not in chat.

**4. Redeploy and test.** Deploy the app with the new key and check that it works.

**5. Look for damage.** Check the provider's logs and your bills for the time the key was exposed. Look for usage you do not recognize, new users, changed data, new keys or new resources. If you find any, treat it as a break-in, not just a leak: check your database, your accounts and your connected apps.

**6. Clean up the code and history.** Remove the key from your code. If it was committed, removing it from git history takes special tools; GitHub's guide uses git-filter-repo. It warns that forks keep the data, old clones can push it back, and you must contact GitHub Support to remove cached views [[github-remove-sensitive]]. This is why step 1 comes first.

**7. Stop it from happening again.** Add a secret scanner before commits and pushes ({{ch:ch-secrets}}), and write down what happened and what you changed.

### Other kinds of "something leaked"

**Your host or a tool you use reports an incident.** Rotate every key stored there that was not protected as a secret, as Vercel advised in April 2026 ({{ch:ch-allow-all}}). Read the provider's bulletin to the end, and follow its updates.

**A package you use was poisoned.** If you installed an affected version, assume that everything the install could reach was read: keys in `.env` files, cloud credentials, tokens for GitHub and npm. CISA's advice after Shai-Hulud was to "immediately rotate all developer credentials" [[cisa-shai-hulud]]. Then install a known-good version.

**Your framework had a critical flaw, and your app was online.** Patch, then rotate the keys the app uses, most important first ({{ch:ch-react2shell}}).

**Your AI agent did something destructive.** Stop the agent. Do not let it "fix" its own mistake until you understand what happened. Restore from a backup you control ({{ch:ch-backups}}). Then check what access the agent had, and reduce it.

**You pasted a key into an AI chat.** Treat it as leaked. Chats are stored, and you cannot be sure where the text goes next. Rotate the key.

### Keep a leak card

Write down, on one page, before you need it:

- every key your app uses, and the exact page where each one is revoked;
- who to contact at each provider, and their security page;
- where your backups are, and how to restore them.

When something leaks, you will be stressed and in a hurry. The card does the thinking for you.

::: {.box .do-this}
**Do this**

- Revoke or rotate first, before anything else.
- Check logs and bills for the exposure window.
- Clean history only after the key is dead.
- After a poisoned package or a framework flaw, rotate every key the affected machine could reach.
- Keep a one-page leak card with every key's revoke page.
:::
