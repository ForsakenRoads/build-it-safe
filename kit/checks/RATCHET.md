# The ratchet: new findings fail, old ones are recorded

A **ratchet** turns only one way. Here it means: a scan never gets worse. Findings that already exist are written down once (a **baseline**), so the check passes today; any **new** finding fails. You then fix the old ones over time instead of switching the check off.

This recipe uses each tool's own baseline feature. No extra program is needed.

## gitleaks (secrets)

Record today's findings (values are redacted):

```sh
gitleaks git --redact --report-format json --report-path .gitleaks-baseline.json --exit-code 0 \
  --log-opts="--no-color --full-history --all" .
```

The `--no-color` matters: if your git config forces colour on, gitleaks reads coloured output and finds nothing.

The kit's git hooks and CI workflow use `.gitleaks-baseline.json` automatically when it exists (`--baseline-path`). Commit the file.

**A baselined key is still a leaked key.** The baseline only stops old findings from blocking work. Revoke every key in it at its provider, then remove the entries as you clean up.

## Code scanners with their own baselines

| Tool | Record the baseline | Check against it |
|---|---|---|
| detect-secrets (Apache-2.0) | `detect-secrets scan > .secrets.baseline` | `detect-secrets-hook --baseline .secrets.baseline` |
| bandit (Apache-2.0, Python) | `bandit -r . -f json -o .bandit-baseline.json` | `bandit -r . -b .bandit-baseline.json` |
| semgrep CE (LGPL-2.1) | on pull requests, compare with the base branch | `semgrep scan --baseline-commit "$BASE_SHA"` |
| ruff (MIT, Python) | `ruff check --add-noqa .` once | `ruff check .` |

## Rules that keep the ratchet honest

- **Fail closed.** If a scanner cannot run or its output cannot be read, the check fails. A crash must never count as "zero findings".
- **Compare findings, not counts.** Fixing one finding while adding another is still a new finding. Baselines that store fingerprints (gitleaks, detect-secrets, bandit) do this; a plain count does not.
- **Suppression comments are changes too.** A new `# noqa`, `# nosec` or `gitleaks:allow` needs a reviewer's approval like any other change.
- **Agents may not edit baselines.** The guard blocks `--no-verify`; reviewers should also look closely at any pull request that touches a baseline file.
