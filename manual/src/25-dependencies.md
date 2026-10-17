## Dependencies {#ch-dependencies}

::: {.dek}
Every package you install is code from a stranger, and some of it runs at once.
:::

### The mental model: you are hiring the whole crew

When you add one package to your project, you also add every package it uses, and every package those use. A small web app can pull in hundreds. Each one was written by someone you have never met, and each one is updated by whoever holds its publishing key.

Most of that code is honest, and you could not build without it. But {{ch:ch-installing}} showed what happens when a publishing key is stolen: a poisoned version goes out, and everyone who installs it runs the attacker's code. Some packages run code the moment you install them, through **install scripts**, before you have even opened your app.

OWASP added "Software Supply Chain Failures" as the third item in its 2025 list of top web risks [[owasp-top10-2025]].

### Lockfiles: install the same thing every time

A **lockfile** (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `poetry.lock`, `uv.lock`) records the exact version of every package your project uses, including the hidden ones. With a lockfile, your computer, your teammate's computer and your server all install the same code. Without it, each install may quietly pick up newer versions, including a poisoned one released an hour ago.

- Commit your lockfile to git.
- On servers and in automated builds, install exactly what the lockfile says. For npm, that command is `npm ci`. It "will exit with an error, instead of updating the package lock" if the two disagree [[npm-ci]].

### Check a package before you install it

AI models sometimes recommend packages that do not exist, and attackers register those names ({{ch:ch-installing}}). Before you install a package your assistant suggests, open its page on the official registry (npmjs.com for JavaScript, pypi.org for Python) and check [[openssf-concise]]:

- **It exists,** and the name is spelled exactly as you expect.
- **The publisher is who you expect,** often the company or project that makes it. Official packages often sit under the company's name, such as `@stripe/…`.
- **It links to a real source repository** with recent activity and more than one maintainer.
- **It is widely used,** with many downloads, and it is not brand-new.

Then ask your agent why it needs the package. Often the standard library, the code that comes with your language, already does the job.

### Wait before taking brand-new versions

Malicious versions are usually caught and removed within hours. pnpm's documentation says: "In most cases, malicious releases are discovered and removed from the registry within an hour" [[pnpm-resolution]]. So a short wait before installing any brand-new version protects you from most of them. As of October 2026:

- **pnpm** has a `minimumReleaseAge` setting, in minutes. Since pnpm 11 it defaults to 1,440 minutes, one day [[pnpm-resolution]].
- **npm** has `min-release-age`, in days: "only versions that were available more than the given number of days ago will be installed" [[npm-config]].

The exception is a security fix for a flaw that is being attacked right now, as with React2Shell ({{ch:ch-react2shell}}). Install that one the same day.

### Control install scripts

Install scripts are the shortest path from a poisoned package to your keys. As of October 2026:

- **pnpm** does not run dependencies' build scripts unless you allow them. Packages not listed in its `allowBuilds` setting "are disallowed by default and are treated as unreviewed" [[pnpm-build]]. PostHog moved to pnpm 10 after Shai-Hulud for this reason [[posthog-shai-hulud]].
- **npm** runs dependencies' install scripts by default, with a notice for any it has not been told to allow. The setting `strict-allow-scripts=true` makes the install fail instead. `ignore-scripts=true` turns all scripts off, which can break packages that need a build step [[npm-config]].

### Keep up with fixes

Known flaws in packages are listed in public databases. Free tools compare your lockfile against them:

- `npm audit` lists known flaws in your dependencies [[npm-audit]].
- **Dependabot**, built into GitHub, alerts you to known flaws, on every GitHub plan [[gh-advanced-security]]. Its security updates can also open pull requests that update a flawed package for you [[gh-dependabot-updates]].
- **OSV-Scanner**, from Google, does the same for many languages [[osv-scanner]].

These find *known* flaws. They do not find a brand-new malicious package. That is what the checks and the waiting period above are for.

### Common AI-assistant mistakes

- Installing a package with a plausible name that does not exist, or that a stranger registered.
- Adding a large package for one small function.
- Deleting the lockfile to "fix" an install error.
- Running `npm audit fix --force`, which can install major upgrades that break your app [[npm-audit]].
- Telling you to run a script straight from the internet with `curl … | bash`, which runs code you have not read.

::: {.box .ask-agent}
**Ask your agent**

"Before you add any package, tell me its exact name, its publisher, its weekly downloads, when its latest version was published, and why we need it instead of the standard library. Then wait for my yes."
:::

::: {.box .do-this}
**Do this**

- Commit your lockfile, and install with `npm ci` (or your tool's equivalent) on servers.
- Check every new package's page before installing it.
- Set a waiting period for new versions (`minimumReleaseAge` or `min-release-age`).
- Block install scripts you have not reviewed.
- Turn on Dependabot, and patch critical flaws the same day.
:::
