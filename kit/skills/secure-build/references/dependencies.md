# Dependencies: every package runs code

Installing a package downloads someone else's code and, often, runs it on the spot. A package can steal keys the moment it installs.

- In August 2025 malicious versions of the Nx build tool, live for about 4 hours, stole tokens, SSH keys and `.env` files. They also ran installed AI command-line tools with their safety checks switched off (`claude --dangerously-skip-permissions`, `gemini --yolo`, `q chat --trust-all-tools`) to search the disk for more secrets.
- The Shai-Hulud worm (September and November 2025) spread through npm by stealing maintainers' tokens and publishing infected versions of their other packages.
- AI models invent package names. A USENIX Security 2025 study found invented names in at least 5.2% of commercial models' suggestions and 21.7% of open-source models'. Attackers register those names ("slopsquatting").

## Before adding a package

1. Say its exact name and why it is needed. Prefer the standard library or a package the project already uses.
2. Confirm it exists on the official registry (npmjs.com, pypi.org, crates.io) and is the one intended: right publisher, a linked source repository, real download numbers, recent activity, more than one maintainer if possible. Watch for look-alike names.
3. Avoid versions published in the last few days. npm 11.10+ supports `min-release-age` (days); pnpm has `minimumReleaseAge`.
4. Install with the project's package manager so the lockfile records the exact version. Commit the lockfile.
5. Do not run a package's suggested `curl … | sh` installer. The guard blocks it.

## Install scripts

- pnpm 10 and later do not run dependencies' install scripts by default.
- npm can be set to `ignore-scripts=true`, which may break packages that need a build step; enable the few that need it.

## Keeping up to date

- Turn on Dependabot alerts and security updates (the kit ships `.github/dependabot.yml`), and the dependency-review check on pull requests.
- When a critical advisory hits your framework, patch the same day. After React2Shell (CVE-2025-55182, December 2025), Vercel advised rotating every secret of any app that was online and unpatched.
- `npm audit` lists known vulnerabilities. `npm audit fix --force` can install breaking major versions; do not run it without the human.

## What you do

- [ ] Name every new dependency and the reason in your summary.
- [ ] Check the registry page before installing; never install a name you have not confirmed exists.
- [ ] Never edit the lockfile by hand; never delete it to "fix" an install.
- [ ] No `curl | sh`, no global installs, no `sudo npm install` unless the human asks.

## Sources

- Nx post-mortem: https://nx.dev/blog/s1ngularity-postmortem
- Snyk on the Nx AI-CLI abuse: https://snyk.io/blog/weaponizing-ai-coding-agents-for-malware-in-the-nx-malicious-package/
- CISA alert on the npm worm (23 Sep 2025): https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem
- Spracklen et al., "We Have a Package for You!" (USENIX Security 2025): https://arxiv.org/abs/2406.10279
- OpenSSF Concise Guide for Evaluating Open Source Software: https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software
- npm config (`min-release-age`, `ignore-scripts`): https://docs.npmjs.com/cli/v11/using-npm/config
- pnpm settings: https://pnpm.io/settings/dependency-resolution
- React2Shell, Vercel bulletin: https://vercel.com/kb/bulletin/react2shell
