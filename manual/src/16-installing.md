## When installing means running {#ch-installing}

::: {.dek}
Every package you add can run code on your computer, with your keys in reach.
:::

### What happened

**Nx: malware that drove the victim's own AI.** Nx is a popular build tool for JavaScript projects. In August 2025 attackers published malicious versions of it to npm, the main public registry of JavaScript packages. The bad versions were "active for 4 hours before being completely removed from the registry" [[nx-postmortem]]. Installing one ran a script that looked for tokens, SSH keys and `.env` files (files that hold secrets), then uploaded what it found to a new public repository in the victim's own GitHub account [[nx-postmortem; wiz-s1ngularity]].

The twist: the malware looked for AI coding tools already installed on the computer, and ran them with their safety checks switched off: `claude --dangerously-skip-permissions`, `gemini --yolo` and `q chat --trust-all-tools`. Its prompt began: "You are a file-search agent." It asked the AI to find files holding keys and settings [[snyk-nx]]. The attacker did not need to write a file-search program. The victim's own AI assistant was the search program.

Wiz counted "over a thousand valid Github tokens" and "dozens of valid cloud credentials and NPM tokens" in the leaked data. In a second phase, the attackers used stolen tokens to make private repositories public: "over 400 users/organizations impacted" and "over 5500 private repositories published publicly" [[wiz-s1ngularity]].

**Shai-Hulud: a worm.** In September 2025 a self-spreading program hit npm. It stole each victim's credentials, then used their npm access to publish infected versions of their other packages. The US Cybersecurity and Infrastructure Security Agency (CISA) counted "over 500 packages" [[cisa-shai-hulud]]. A second wave in November hit packages from well-known companies, including Zapier, PostHog and Postman [[wiz-shai-hulud-2]].

**Slopsquatting: names that AI invents.** AI models sometimes recommend packages that do not exist. A study presented at USENIX Security 2025 tested 576,000 code samples from 16 models. Invented package names appeared in at least 5.2% of commercial models' suggestions and 21.7% of open-source models', 205,474 unique made-up names in all [[spracklen-packages]]. An attacker can register an invented name and fill it with malware. In January 2026 the security company Aikido found "react-codeshift", a name that did not exist, in "a single commit of 47 LLM-generated Agent Skills". It "had spread to 237 repositories through forks". Aikido registered the name first, and AI agents still try to install it [[aikido-slopsquatting]].

**Amazon Q: a wiper inside an official tool.** In July 2025 AWS shipped version 1.84.0 of its Amazon Q Developer extension for the VS Code editor with malicious instructions inside. AWS says "an inappropriately scoped GitHub token" let an attacker commit the code, which went straight into a release. The code was "unsuccessful in executing due to a syntax error", which AWS says "prevented the malicious code from making changes to any services or customer environments". AWS fixed it in version 1.85.0 [[aws-q-bulletin]]. According to CSO Online, the code "instructed the AI agent to behave like a system cleaner with access to the file system and cloud tools, aiming to erase user data and cloud resources" [[cso-amazon-q]].

### Why it happened, in plain words

::: {.box .plain-words}
**Plain words**

- **Package (or dependency):** code written by someone else that your project downloads and uses. A typical web app uses hundreds of them, most pulled in by other packages.
- **Install script:** a small program inside a package that runs automatically when you install it, with your permissions.
- **Supply chain attack:** an attack on something you trust and download, instead of on you directly.
:::

Installing a package is not like downloading a document. Many packages run code the moment they install, on your computer, with access to everything you can access: your files, your keys and your logged-in tools. You are trusting every author of every package, and every person who could steal their publishing keys.

The two big npm attacks began with stolen publishing keys. Nx's own automation pasted an unchecked pull-request title into a command, which let the attacker steal Nx's npm token [[nx-postmortem]]. PostHog traced its own compromise to a similar automated workflow that ran code from outside contributors [[posthog-shai-hulud]].

AI tools add two new risks. They can invent package names that attackers then claim. And a powerful AI assistant on your computer, left in a no-questions-asked mode, is a tool that malware can use against you.

::: {.box .lesson}
**The lesson**

- Before installing a package an AI suggests, check that it exists, that it is the one you meant, that many people use it, and that it is not brand-new ({{ch:ch-dependencies}}).
- Commit your lockfile, wait before taking brand-new versions, and turn off install scripts where you can ({{ch:ch-dependencies}}).
- Do not leave AI coding tools in "skip permissions" or "yolo" mode by default ({{ch:ch-agent}}).
- After any alert about a package you use, rotate your keys ({{ch:ch-leak}}).
:::
