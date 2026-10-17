## "Allow All": the breach that began at a small AI tool {#ch-allow-all}

::: {.dek}
Every app you connect to your accounts is a door into them.
:::

### What happened

On 19 April 2026, Vercel disclosed a security incident. Its bulletin traces the path step by step. The incident "originated with a compromise of Context.ai, a third-party AI tool used by a Vercel employee." The attacker "used that access to take over the employee's individual Vercel Google Workspace account", and from there reached "that employee's Vercel account". Then the attacker "maneuvered through systems to enumerate and decrypt non-sensitive environment variables" [[vercel-april-bulletin]].

Context.ai sold an "AI Office Suite". It said that "at least one Vercel employee signed up for the AI Office Suite using their Vercel enterprise account" and granted "Allow All" permissions. Context.ai also said it had blocked unauthorized access to its own cloud systems in March 2026 [[thn-vercel-context]]. Context.ai's statement no longer loads at the address the press linked to, so this comes from press coverage of it [[context-statement]].

How did Context.ai get hacked? The threat-intelligence company Hudson Rock reported that a Context.ai employee's computer was infected in February 2026 with Lumma, a password-stealing program, and that this may have been how the attack began. Hudson Rock's records showed the user "actively searching for and downloading game exploits, specifically Roblox 'auto-farm' scripts", a common way that kind of malware spreads [[thn-vercel-context; cyberscoop-vercel]].

Vercel first said "a limited subset of customers" was affected, and later added "a small number of additional accounts". It said "no npm packages published by Vercel have been compromised". It told customers to rotate every environment variable not marked "sensitive", to turn on multi-factor sign-in, and to review their activity logs. On 16 October 2026 the bulletin said that "all remediation actions related to the security incident are complete, and the incident is closed" [[vercel-april-bulletin]].

A group calling itself ShinyHunters claimed the attack on Telegram and tried to sell data that it said included "access keys, source code and databases". An analyst at Google's threat-intelligence group said the attacker "is likely an imposter attempting to use an established name to inflate their notoriety" [[cyberscoop-vercel]]. Those claims remain unconfirmed.

### Why it happened, in plain words

::: {.box .plain-words}
**Plain words**

- **"Sign in with Google" and "Allow":** when an app asks to connect to your Google, GitHub or Microsoft account, and you click Allow, you give that app a token. A token is a standing key that lets the app act on your account until you take it back.
- **Malware:** software written to harm you, such as a program that steals saved passwords from your browser.
:::

This was a chain of four links:

1. According to Hudson Rock, one person at a small company downloaded game cheats, and malware came with them.
2. An attacker got into that company's cloud systems, which held tokens that its users had granted. Hudson Rock says the malware may have opened that door.
3. One of those users, at Vercel, had clicked "Allow All" for the small AI app, using a work account. The stolen token opened that work account.
4. From the work account, the attacker reached Vercel's internal systems and decrypted customer settings that were not marked sensitive.

No link needed a genius. Each one was an ordinary decision: a download, a stored token, a click on Allow, a setting left at its default. The chain worked because nobody broke it.

There is a second lesson for anyone who hosts on Vercel. The bulletin says the attacker decrypted variables that were *not* marked sensitive, and it recommends the sensitive-variables feature so that secret values are protected from being read in future [[vercel-april-bulletin]]. As of October 2026, Vercel calls every variable either **Config** or **Secret**. Secret values are write-only: members "cannot view or retrieve it after saving". Variables that were marked "Sensitive" became Secrets automatically [[vercel-secret-vars; vercel-config-secret-changelog]].

::: {.box .lesson}
**The lesson**

- Mark every secret on your host as secret (on Vercel, the Secret type). Leave nothing secret as a plain setting ({{ch:ch-secrets}}).
- When your host reports an incident, rotate your keys first and ask questions later ({{ch:ch-leak}}).
- Refuse "Allow All" for small or new apps, and never use a work account to try one. Review your connected apps every month ({{ch:ch-accounts}}).
- Turn on multi-factor sign-in everywhere, and use passkeys where you can ({{ch:ch-accounts}}).
:::
