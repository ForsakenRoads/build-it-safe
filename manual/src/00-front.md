# About this edition {#about .matter .unnumbered}

*{{MAIN_TITLE}}: {{SUBTITLE}}*, by {{AUTHOR}} ([{{HANDLE}}]{.nohyph} on X). Draft of October 2026.

{{ATTRIBUTION}}

::: {.attribution-note}
{{ATTRIBUTION_NOTE}}
:::

Licensed under CC BY-ND 4.0: share it freely, with credit, unchanged. See `LICENSING.md`.

Everything in this book was checked against its sources in October 2026. Prices, plan features and product names change often; each is marked "as of October 2026" where it matters. The numbered notes lead to the Sources appendix, where every source is listed with its address.

Found a mistake, or a source that has changed? Send a direct message to [{{HANDLE}}]{.nohyph} on X, with the page and a source. Report security problems in the kit privately: through the repository's private vulnerability reporting, or by email to security@forsakenroads.com (see `SECURITY.md`).

This book names companies and products only to describe what they do, or what happened to them. No company paid to appear in it, and it contains no referral links. The example keys in this book are fake, and labeled as such.

# Why this exists {#why .matter .unnumbered}

In March 2025, the founder of a small paid web app posted that it had been "built with Cursor, zero hand written code". Two days later he posted: "guys, i'm under attack". Strangers had "maxed out usage on api keys" and were "bypassing the subscription" [[cendyne-vibe]]. Three days after that, he posted that he was shutting the app down [[x-enrichlead-shutdown]].

At the end of January 2026, researchers at Wiz read the code that Moltbook, a viral social network for AI agents, sent to every visitor. In it was the key to its database, which had no access rules. Anyone could read and change every table, including "1.5 million API authentication tokens" and "35,000 email addresses" [[wiz-moltbook]].

In July 2025, an AI agent on Replit deleted a company's production database during a code freeze, after its user said he had "explicitly told it eleven times in ALL CAPS not to do this" [[register-replit]]. Replit's CEO called it "Unacceptable and should never be possible" [[x-masad-replit]].

In April 2026, the hosting company Vercel disclosed a breach that "originated with a compromise of Context.ai, a third-party AI tool used by a Vercel employee" [[vercel-april-bulletin]]. According to Context.ai, the employee had signed up with a work account and granted it "Allow All" [[thn-vercel-context]]. The attacker went on to decrypt customers' settings that were not marked sensitive [[vercel-april-bulletin]].

In August 2025, malicious versions of the popular build tool Nx looked for AI coding assistants on their victims' computers, and ran them with their safety checks switched off, as search tools for keys and settings [[snyk-nx]].

And when a security company planted working keys in public code, attackers used them after 6.6 minutes on average [[clutch-rotation]].

None of these needed a genius. Each one turned on an ordinary decision: a key in the wrong place, a database without rules, an agent with access to production, one click on "Allow", a no-questions mode left switched on. Each one also has a simple defense, which experienced engineers learned the hard way and anyone can learn in an afternoon.

{{MAIN_TITLE}} is a project of {{AUTHOR}} to improve safety and security for developers who use machine intelligence to code and release projects. This book and its companion kit exist so that anyone who builds with AI can avoid these mistakes, before they cost a database, a bill or a reputation.

# How to read this book {#how-to-read .matter .unnumbered}

You do not have to read it all at once. There are three ways in.

**The one-hour essentials.** If you are about to launch something, start with the "Start here" card on the next page: four chapters and one checklist.

**The full read.** Part I tells eight true stories of things going wrong, two pages each. Part II explains the fundamentals, one idea per chapter, with the practice and a short checklist. Part III gathers the checklists, the rules to give your AI agent, and the steps to install the companion kit.

**The checklists.** If you already know the ideas, go straight to {{ch:ch-checklists}} and tick the boxes. Each item points back to the chapter that explains it.

**How the book is laid out.** Every technical term is explained the first time it appears, and again in the Glossary. Four kinds of boxes appear throughout:

- **Plain words** define terms.
- **Do this** lists the actions to take.
- **Ask your agent** gives a prompt you can paste into your AI assistant.
- **Watch out** marks the one trap to avoid.

Small numbers in the text lead to the Sources appendix. You do not need to read them, but every claim in this book can be checked.

# Start here {#start-here .matter .unnumbered}

If you read nothing else before you launch, read these, in this order. Together they take about an hour, and they prevent most of the stories in Part I.

::: {.box .do-this .start-card}
**Start here: the one-hour essentials**

- **Keys stay on the server.** Anything sent to the browser is public. Move every secret out of public variables and out of your code ({{ch:ch-secrets}}).
- **Every table has a lock.** Turn on row-level security or security rules, then test as a logged-out stranger and as a second user ({{ch:ch-doors}}).
- **Every paid service has a cap.** Set a hard cap where one exists, set alerts low, and act on every alert ({{ch:ch-money}}).
- **Revoke first.** If a key leaks, cancel it at the provider before you do anything else ({{ch:ch-leak}}).
- **Tick the launch checklist.** Go through "Before you launch" in {{ch:ch-checklists}}, box by box.
:::

Then, when you have time: read Part I for the stories behind these rules, and {{ch:ch-agent}} before you give an AI agent more power.
