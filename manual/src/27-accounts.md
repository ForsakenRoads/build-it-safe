## Accounts {#ch-accounts}

::: {.dek}
Your accounts are the master keys to everything you build.
:::

### The mental model: the keyring

Your GitHub, Google, hosting, database and payment accounts are a keyring. Whoever holds one of them can usually change your code, read your data, spend your money and lock you out. Every app you have connected to them hangs on the same ring. The Vercel breach in {{ch:ch-allow-all}} started with one small app on one employee's ring.

Protecting accounts takes four habits: strong sign-in, unique passwords, a short list of connected apps, and owning your names.

### Strong sign-in: passkeys and multi-factor

::: {.box .plain-words}
**Plain words**

- **Multi-factor authentication (MFA):** signing in with your password *plus* something else, such as a code from an app on your phone. A stolen password alone is then not enough.
- **Phishing:** a fake website or message that tricks you into typing your password or code.
- **Passkey:** a sign-in method that uses a secret stored on your phone or computer instead of a password. It works only on the real website, so a fake site cannot use it.
:::

Not all second factors are equal. A code sent by text message or typed from an app can be typed into a fake website too. A passkey or a hardware security key cannot, because it checks which website is asking. AWS recommends "phishing-resistant MFA such as passkeys and security keys" [[aws-iam-best]]. CISA, the US cybersecurity agency, has called FIDO/WebAuthn, the standard behind passkeys and security keys, "the only widely available phishing-resistant authentication" [[cisa-mfa]].

Turn on the strongest option each service offers, starting with the accounts that hold the most: your email (it can reset every other password), GitHub, your host, your database and your payment provider. Save the recovery codes somewhere safe and offline.

### A password manager

A **password manager** is an app that creates a different long, random password for every site and fills it in for you. If one site leaks its passwords, the leak does not open your other accounts. Many password managers also store passkeys. Use one, and protect it with your strongest sign-in.

### Review your connected apps

Every "Sign in with Google" or "Connect to GitHub" you ever clicked may still be active. Review them every month, and remove anything you do not use or do not recognize:

- **Google:** your account's linked apps page, `myaccount.google.com/linkedapps`. Choose "Access to your Google Account", select an app, choose "See details", then "Remove access" and "Confirm" [[google-linked-apps]].
- **GitHub:** Settings → Applications → "Authorized OAuth Apps", then "Revoke" next to anything you do not need. GitHub Apps have their own tab on the same page [[github-oauth-review]].

When a new app asks for access, read what it asks for. "See your email address" is small. "Read, compose, send and permanently delete all your email", or "Allow All", is the whole keyring. Never connect a work account to a tool you are only trying out.

### Claim your names

Your names are part of your security, because people and tools trust them.

- **Account and repository names.** If you rename or delete a GitHub account, someone else can register the old name and recreate your repository names. Old links, and old install commands, then fetch *their* code. GitHub protects popular repositories against this, but researchers found ways around that protection in 2023, since fixed [[checkmarx-repojacking]]. Do not rename accounts that others depend on, and if you must, keep the old name reserved.
- **Package names.** If you publish packages, claim your name on the registries you use (for example, an npm scope such as `@yourname`), even before you need it.

### Tokens for publishing

If you publish packages, your publishing token is a key to everyone who installs your work. After the Shai-Hulud worm, npm stopped issuing its older "classic" tokens in November 2025 and revoked the remaining ones in December [[npm-classic-disabled; npm-classic-revoked]]. Its newer tokens that can publish now require two-factor sign-in by default and last at most 90 days [[npm-classic-disabled]]. Better still is "trusted publishing", which lets your automated build publish without any long-lived token; npm says to "always prefer it over long-lived tokens" [[npm-trusted-publishing]]. Nx moved to trusted publishing after its incident [[nx-postmortem]].

### Common AI-assistant mistakes

- Creating a personal access token with every permission and no expiry date.
- Suggesting you connect a broad "all access" integration when a narrow one exists.
- Storing a publishing token in a file in the repository.

::: {.box .do-this}
**Do this**

- Turn on passkeys or a security key for email, GitHub, your host, your database and your payment accounts. Use an authenticator app where those are not offered.
- Use a password manager, with a unique password for every account.
- Review connected apps on Google and GitHub every month, and refuse "Allow All".
- Keep your account and package names, and do not rename accounts others depend on.
- If you publish packages, use trusted publishing instead of long-lived tokens.
:::
