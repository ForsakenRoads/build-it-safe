# Contributing

Thank you for helping. This project is **moderated open source**: anyone may propose a change, and maintainers review every change before it is merged. People rely on a security guide being right, and a wrong instruction can cost someone their data or their money, so every change gets a careful human review.

## Who can contribute, and who reviews

- **Anyone may propose a change.** Open an issue or a pull request; every proposal is read.
- **Only vetted professionals who volunteer review and merge.** Forsaken Roads® gives reviewer or maintainer rights only after checking who the person is and their record. Asking for rights is welcome, but they are never given on request alone.
- **Changes to agent-facing files** (the rules block, the skill and its reference pages, the manual's agent-rules chapter) always need two approvals, one of them the owner's.
- **Forks are not the official project.** If you publish a fork, say clearly that it is a fork and link to the original (see `TRADEMARKS.md`).

## The rules

1. **Every factual claim needs a source.** Link the primary source (the vendor's documentation, the advisory, the researcher's own write-up, the paper) next to the claim. News coverage is acceptable only when there is no primary source, and must be labelled as such. Numbers are quoted exactly as the source gives them, with who measured them and when.
2. **Time-sensitive facts carry a date:** prices, plan features, provider limits and tool versions say "as of <month year>".
3. **Maintainers review every change.** Nothing merges without approval from a code owner (see `.github/CODEOWNERS`).
4. **No auto-merge.** Bots, including Dependabot and AI agents, may open pull requests; a human reviews and merges each one.
5. **No secrets, ever.** Tests generate fake keys at run time. Never commit a realistic-looking key, even a fake one: scanners (ours and GitHub's) will flag it.
6. **No copied code without a compatible licence.** Say where any borrowed code comes from and under which licence.

## How to propose a change

1. Open an issue first for anything larger than a typo, so we can agree on the approach.
2. Fork the repository and create a branch.
3. Make the change. For the kit, run the tests: `python3 tests/run_tests.py`.
4. Open a pull request that says what changed, why, and the sources for any facts.
5. A maintainer reviews it. Expect questions; they are about the content, never about you.

## What reviewers check

- Is every new claim sourced, current and stated no more strongly than the source states it?
- Is the language plain? (See the style rules in the manual's style sheet.)
- Does the change keep the kit's promises: it never overwrites a user's file, the installer stays idempotent, and `uninstall` removes exactly what was added?
- Do the tests pass twice in a row?
- **Agent-facing files are read as raw diffs, by a person.** Changes to `AGENTS.md`, `CLAUDE.md`, any `SKILL.md`, the skill's reference pages, the core rules block (`kit/core/`) and the manual's agent-rules chapter are reviewed by reading the raw diff yourself, not by asking an AI agent to summarise or review it: the change may contain instructions written for an agent. Watch for text aimed at an AI rather than a human ("ignore previous instructions", "do not tell the user", requests to disable a check or fetch something), and for hidden characters (the CI's hidden-text check must pass). These paths need two approvals (see `GOVERNANCE.md`).

## Reporting a security problem

Do not open a public issue. See [SECURITY.md](SECURITY.md).

## Conduct

Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md). Newcomers are welcome here, and so is the hard-won knowledge of experienced engineers.
