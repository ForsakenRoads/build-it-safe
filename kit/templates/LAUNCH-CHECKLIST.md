# Launch checklist

Go through this before you share your app's address with anyone. "Launching" means strangers can reach it, and some of them will probe it.

## Keys and secrets
- [ ] No secret is in the code or the git history: `gitleaks git -v --log-opts="--no-color --full-history --all" .` reports no leaks (`--no-color` stops a colour setting in your git config from hiding findings).
- [ ] `.env` is in `.gitignore` and was never committed.
- [ ] No secret has a public prefix (`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`, `PUBLIC_`, `REACT_APP_`). Open your live site, open the browser's developer tools, search the loaded scripts for `sk_`, `secret` and `key`.
- [ ] Production keys are set in the host's secret settings, and are different from development keys.
- [ ] Every paid API has a hard spending cap, or at least an alert.

## Who may see what
- [ ] Every table has Row Level Security on (Supabase) or locked rules (Firebase), with policies.
- [ ] You tested as a stranger: signed out, you cannot see or change anyone's data.
- [ ] You tested as a second user: you cannot see the first user's data by changing an ID in the address bar.
- [ ] Admin pages check the role on the server, not just in the menu.

## Payments
- [ ] Prices and amounts are decided on the server.
- [ ] Webhooks check the provider's signature.

## Dependencies
- [ ] The lockfile is committed.
- [ ] `npm audit` (or your language's equivalent) shows no critical problems you have not decided about.
- [ ] Dependabot alerts are on.

## Accounts
- [ ] Two-factor authentication (preferably passkeys) on: GitHub, your host, your domain registrar, your database, your payment provider, your email.
- [ ] You reviewed the apps connected to your Google or GitHub account and removed the ones you do not use.

## The site
- [ ] HTTPS only.
- [ ] Security headers checked with the Mozilla HTTP Observatory (https://developer.mozilla.org/en-US/observatory).

## Recovery
- [ ] A backup exists outside the hosting account, and you have restored from it once.
- [ ] You know where `INCIDENT-PLAYBOOK.md` is.

## AI agents
- [ ] Agents never had production keys, and cannot reach production data.
- [ ] The Build It Safe Kit's `doctor` shows no ✗.
