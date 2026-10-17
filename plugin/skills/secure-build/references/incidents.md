# When something leaks

If a key, token or password may have been exposed (committed, pushed, printed in a log or chat, pasted into a web page, sent to a tool), treat it as stolen. Attackers find leaked keys within minutes.

## Revoke first

1. **Stop and tell the human now.** Name the key by its variable name and provider. Never repeat its value.
2. **The human revokes or rotates the key at the provider**, in the provider's dashboard. This is the only step that makes the leaked copy useless. Removing it from code does not.
3. **Create the replacement** with the smallest permissions that work, and put it in `.env` and the host's secret store, never in code.
4. **Redeploy** and check the app works with the new key.
5. **Check the damage:** the provider's logs and bills for the time the key was exposed; unknown resources, users, deployments or charges.
6. **Clean up:** remove the key from the code. If it was committed, it stays in history: GitHub's guide uses `git filter-repo` (v2.47+ with `--sensitive-data-removal`), and forks and old clones keep copies, which is why step 2 comes first.
7. **Prevent a repeat:** make sure gitleaks runs on commit and push, and that the file is in `.gitignore`.

## Other incidents

- **A malicious package was installed** (an advisory names a version you have): stop, tell the human, and rotate every credential the machine had: npm, GitHub, cloud, SSH and AI keys. CISA's advice after the 2025 npm worm was to "immediately rotate all developer credentials".
- **Your framework has a critical advisory:** patch the same day. If the app was exposed while unpatched, assume its environment variables were read and rotate them.
- **Strange charges:** treat as a leaked key until shown otherwise.
- **Data deleted:** stop all writes, tell the human, and restore from a tested backup. Do not "fix" it by recreating data.

## What you do

- [ ] Say exactly what may have leaked and where, without the value.
- [ ] Do not try to hide or quietly rewrite history; the human decides.
- [ ] Follow the human's lead; offer the steps above.

The kit's `INCIDENT-PLAYBOOK.md` template is the human's version of this page.

## Sources

- GitHub, removing sensitive data: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Stripe key rotation: https://docs.stripe.com/keys
- CISA alert (23 Sep 2025): https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem
- React2Shell, Vercel bulletin: https://vercel.com/kb/bulletin/react2shell
- Clutch Security, leaked-key test: https://www.clutch.security/blog/shattering-the-rotation-illusion-part-1-code-hosting-and-version-control-platforms
