## "Zero hand-written code" {#ch-enrichlead}

::: {.dek}
Launching an app invites strangers to probe it, often within days.
:::

### What happened

In March 2025 the founder of EnrichLead, a paid web app, posted on X that his software "was built with Cursor, zero hand written code" [[cendyne-vibe; snyk-vibe]]. Cursor is an AI coding editor: you describe what you want, and it writes the code.

Two days later, on 17 March, he posted: "guys, i'm under attack", "ever since I started to share how I built my SaaS using Cursor". He listed what he saw: "maxed out usage on api keys, people bypassing the subscription, creating random shit on db". He added: "as you know, I'm not technical so this is taking me longer that usual to figure out" [[x-enrichlead-attack; cendyne-vibe]]. On 20 March he posted that he was shutting the app down: "Cursor just keeps breaking other parts of the code you guys were right, I shouldn't have deployed unsecured code to production" [[x-enrichlead-shutdown]].

These posts are the founder's own words on social media. Nobody published an investigation, so the exact technical causes are not known.

### Why it happened, in plain words

His post names three symptoms. Each one matches a mistake that is common in apps built quickly, by people or by AI:

- **"Maxed out usage on api keys."** An API key is a password that lets a program use a paid service, such as an AI model or a mapping service. Whoever holds it can spend your money. If strangers could use his keys, the keys were probably reachable from outside, for example inside the code that the app sends to every visitor's browser.
- **"People bypassing the subscription."** A paywall checked only in the browser is a suggestion, not a lock. The browser runs on the visitor's computer, and the visitor can change anything that happens there.
- **"Creating random shit on db."** A database that accepts writes from strangers has no working rules about who may add or change data.

These are likely explanations, not confirmed ones. If you read a blog post that states them as fact, check what it cites.

The bigger lesson is about timing. By his own account, the attacks began after he started sharing in public how he built the app, and his "under attack" post came two days after the "zero hand written code" one. Expect the same for your app. Google's Firebase documentation puts it plainly: once you deploy an app, "it's publicly accessible — even if you haven't launched it" [[firebase-rules-basics]]. Strangers do not need an invitation. They need only an address.

::: {.box .lesson}
**The lesson**

- Before you announce an app, keep every key on the server, where visitors cannot see it ({{ch:ch-secrets}}).
- Check payment and permission rules on the server, never only in the browser ({{ch:ch-doors}}).
- Turn on your database's access rules, then test as a stranger ({{ch:ch-doors}}).
- Set a hard spending cap on every paid API, so a stolen key costs you a fixed amount ({{ch:ch-money}}).
:::
