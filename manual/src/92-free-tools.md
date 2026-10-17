# Free tools {#free-tools .matter .unnumbered}

Every tool below is free to use, or has a free plan, as of October 2026. Check each tool's own page before you rely on it; terms change.

| Tool | What it does | Chapter |
|---|---|---|
| gitleaks | Scans changes for keys before commits and pushes. MIT license [[gitleaks-repo]] | {{ch:ch-secrets}} |
| TruffleHog | Scans a project's history for keys, and checks whether they still work [[trufflehog-repo]] | {{ch:ch-secrets}} |
| GitHub push protection | Blocks known key formats in pushes to public repositories; on by default for your own pushes [[github-push-protection]] | {{ch:ch-secrets}} |
| Supabase Security Advisor | Flags tables in the public schema with row-level security switched off, in the Supabase dashboard [[supabase-advisors]] | {{ch:ch-doors}} |
| `npm audit` | Lists known flaws in a JavaScript project's dependencies [[npm-audit]] | {{ch:ch-dependencies}} |
| Dependabot | Alerts about flawed dependencies on GitHub, on every plan [[gh-advanced-security]]; its security updates can open pull requests to fix them [[gh-dependabot-updates]] | {{ch:ch-dependencies}} |
| OSV-Scanner | Checks dependencies against Google's open database of known flaws [[osv-scanner]] | {{ch:ch-dependencies}} |
| restic | Encrypted, open-source backups [[restic-design]] | {{ch:ch-backups}} |
| Let's Encrypt | Free certificates for HTTPS [[letsencrypt-about]] | {{ch:ch-websites}} |
| HTTP Observatory | Checks a site's security headers [[mdn-observatory]] | {{ch:ch-websites}} |
| The companion kit | Rules block, guard hook, skill and checks for your projects | {{ch:ch-kit}} |
