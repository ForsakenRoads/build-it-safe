# Publishing checklist: the day the repository goes public

Do these in order. The repository stays private until step 1 is finished.

## 1. Before you flip it to public

- [x] The name ("Build It Safe"), the company (Forsaken Roads®) and the X handle (@Forsaken_Roads) are decided (16 Oct 2026).
- [x] The licences are chosen (owner, 17 Oct 2026): Apache-2.0 for the code (`LICENSE`, `NOTICE`), CC BY-ND 4.0 for the manual (`manual/LICENSE`); `LICENSING.md` explains them in plain words.
- [ ] `TRADEMARKS.md` has been reviewed by the attorney (it is a draft).
- [ ] Confirm the Code of Conduct's use: `CODE_OF_CONDUCT.md` is the Contributor Covenant 2.1, verbatim; its site states no licence for the text.
- [x] The official repository address, https://github.com/ForsakenRoads/build-it-safe, is in the README, `SECURITY.md`, `NOTICE`, `LICENSING.md` and the plugin and marketplace manifests (`homepage`, `repository`). Claim it on GitHub before publishing.
- [x] `.github/CODEOWNERS` names the owner's GitHub handle. (The contact placeholders are done: `TRADEMARKS.md` and our `SECURITY.md` use the X DM; `kit/templates/SECURITY.md` deliberately keeps a `[YOUR PRIVATE CONTACT]` blank for adopters.) The manifests' author and owner are already "Forsaken Roads".
- [x] Contact method (owner, 16 Oct 2026): security reports through GitHub private vulnerability reporting (switch it on, see below) or security@forsakenroads.com, with a DM to @Forsaken_Roads on X as the fallback; Code of Conduct reports and trademark questions by DM to @Forsaken_Roads. Commits use the pushing account's GitHub noreply address.
- [ ] Scan the whole history: `gitleaks git -v --log-opts="--no-color --full-history --all" .` reports no leaks (`--no-color` stops a colour setting in your git config from hiding findings).
- [ ] Search the history for private names, paths and hosts that must not be published.
- [ ] Scan the agent-facing files for hidden characters by hand: `python3 kit/checks/hidden_text.py --rules` must print nothing and exit 0. It covers `AGENTS.md`/`CLAUDE.md`-style files, every skill file and reference page, the core block and the manual's agent-rules chapter.
- [ ] The tests pass twice in a row: `python3 tests/run_tests.py`.
- [ ] The manual PDF is built at the path the README links to.

## 2. Repository settings (Settings on GitHub)

- [ ] **Branch protection** (a ruleset) on `main`:
  - [ ] require a pull request before merging;
  - [ ] require approval from **code owners**;
  - [ ] dismiss stale approvals when new commits are pushed;
  - [ ] require the `build-it-safe` status checks to pass, and list the hidden-text job ("Hidden characters in agent rules files") as a **required** check by name, next to "Secret scan (gitleaks)";
  - [ ] require two approvals for changes to the agent-facing paths in `GOVERNANCE.md`. If the ruleset can only set one approval count for the whole branch, set it to 2 once there are two maintainers; until then the owner is the code owner for those paths;
  - [ ] **block force pushes**;
  - [ ] block deletion of `main`;
  - [ ] include administrators.
- [ ] **Allow auto-merge: off.**
- [ ] **Actions:** require approval for workflows from first-time contributors; set the default `GITHUB_TOKEN` permission to read-only.

## 3. Security settings (Settings → Advanced Security)

- [ ] **Secret scanning: on.** Free on public repositories.
- [ ] **Push protection: on.** It stops pushes that contain known key formats.
- [ ] **Private vulnerability reporting: on**, so `SECURITY.md`'s instructions work.
- [ ] **Dependabot alerts and security updates: on.** (`.github/dependabot.yml` handles version updates.)
- [ ] **Dependency graph: on** (needed by the dependency-review check).
- [ ] **CodeQL default setup: on** (Code scanning → CodeQL analysis → Set up → Default). Free on public repositories.

## 4. Releases

- [ ] Tag every release (`claude plugin tag` checks that `plugin/.claude-plugin/plugin.json` and the marketplace entry carry the same version, then creates the tag). Bump both versions in the same commit.
- [ ] Never move or reuse a tag once published.
- [ ] Sign every release tag from the first public release (`git tag -s`), with a key registered on the maintainer's GitHub account, so the tag shows **Verified**.
- [ ] Publish a `SHA256SUMS` file with each release, covering the manual PDF and the release files (`sha256sum <files> > SHA256SUMS`), and check it once from a fresh download.
- [ ] Turn on tag protection for `v*` in the ruleset.

## 5. Accounts

- [ ] Every maintainer has two-factor authentication on, preferably with a passkey or security key.
- [ ] Claim the project's name on npm and PyPI if you might publish packages there later.

## 6. After publishing

- [ ] Add the marketplace in Claude Code from a clean machine and install the plugin (`/plugin install build-it-safe@build-it-safe` after `/plugin marketplace add ForsakenRoads/build-it-safe`); check that the guard blocks reading `.env`.
- [ ] Watch the first outside pull requests closely.

Sources:
- GitHub, about rulesets and protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- GitHub, about secret scanning and push protection: https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection
- GitHub, privately reporting a security vulnerability: https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability
- GitHub, CodeQL default setup: https://docs.github.com/en/code-security/code-scanning/enabling-code-scanning/configuring-default-setup-for-code-scanning
