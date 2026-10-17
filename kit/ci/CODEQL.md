# Turning on CodeQL (code scanning)

CodeQL reads your code and reports common vulnerabilities such as SQL injection and cross-site scripting. The kit does not add a CodeQL workflow, because GitHub's **default setup** does it for you and keeps itself up to date.

As of October 2026:
- **Public repositories:** free. Turn it on in **Settings → Advanced Security → Code scanning → CodeQL analysis → Set up → Default**.
- **Private repositories:** needs GitHub Code Security (a paid add-on). Without it, use a free scanner such as Semgrep's free tier or OSV-Scanner for dependencies.

After you turn it on, results appear under **Security → Code scanning**. Ask a maintainer to review each alert; do not let an agent dismiss alerts on its own.

Source: GitHub, "Configuring default setup for code scanning": https://docs.github.com/en/code-security/code-scanning/enabling-code-scanning/configuring-default-setup-for-code-scanning
