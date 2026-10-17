# Governance

## Roles

- **Owner:** Forsaken Roads®. Decides the project's direction, its name, its licences, and who the maintainers are. Holds the final say on any disagreement.
- **Maintainers:** review and merge pull requests, triage issues, cut releases. They are listed in `.github/CODEOWNERS`. A maintainer is added or removed by the owner.
- **Contributors:** anyone who opens an issue or a pull request.

## Who may do what

- **Anyone may propose a change**, by opening an issue or a pull request.
- **Review and merge rights are given only to vetted professionals who volunteer.** Forsaken Roads® first checks who they are and their record (for example their professional background and a history of careful, sourced contributions here). Rights are never given on request, and Forsaken Roads® can withdraw them.
- A malicious editor could slip bad advice or hidden instructions into a security guide or into files that AI agents obey, so the agent-facing files below always need **two approvals**, one of them the owner's.

Open source does not mean that Forsaken Roads® endorses every copy. Forks are outside this process: Forsaken Roads® reviews and supports only the official repository and the releases published there (see the README, "The official project, and forks", and `TRADEMARKS.md`).

## How decisions are made

- **Content changes** (the manual, except its agent-rules chapter): one maintainer's approval, plus a check that every new claim is sourced.
- **Code changes** (installer, doctor, tests): one maintainer's approval and passing tests.
- **Agent-facing and security-sensitive changes**: two approvals, one of them the owner's. These are the files an AI agent reads and acts on, or that enforce the rules, so a bad edit there does the most harm:
  - the core rules block (`kit/core/`), the skill and its reference pages (`kit/skills/`, and the generated copy in `plugin/skills/`), and the manual's agent-rules chapter (`manual/src/42-agent-rules.md`);
  - the guard (`kit/guard/`), the git hooks (`kit/git-hooks/`), the agent hook settings (`kit/agents/`), the CI workflows (`kit/ci/`, `.github/`), the plugin and marketplace manifests;
  - this file and `.github/CODEOWNERS`.
- **Disagreements:** discussed in the pull request; if unresolved, the owner decides.

## Releases

Releases are tagged by a maintainer after the tests pass twice in a row, with the owner's review. The plugin's version in `plugin/.claude-plugin/plugin.json` and its entry in `.claude-plugin/marketplace.json` always change together, in the same commit; `claude plugin tag` checks that they agree and creates the tag. Once there is more than one maintainer, tags are signed.

## Changes to this document

Changes to governance need the owner's approval.
