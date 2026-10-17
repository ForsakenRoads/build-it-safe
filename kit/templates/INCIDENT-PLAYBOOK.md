# Incident playbook: when something leaks

Print this page, or keep it where you can find it when you are stressed. Work from the top.

A **leak** means a secret (an API key, a token, a password) may have been seen by someone who should not have it: you committed it, pushed it, pasted it into a chat or a web page, printed it in a log, or an alert told you so. Treat a leaked key as stolen. In one test, attackers used keys leaked on GitHub after 6.6 minutes on average (Clutch Security, 2024).

## 1. Revoke first (minutes 0–15)

- [ ] Open the provider's dashboard (Stripe, OpenAI, Anthropic, AWS, Supabase, GitHub …) and **revoke or rotate the key**. This is the only step that makes the leaked copy useless. Deleting it from your code does not.
- [ ] If you are not sure which keys leaked, rotate every key the app or machine had.
- [ ] Turn off the leaked key even if the new one is not ready yet. A short outage costs less than a stolen key.

## 2. Replace (minutes 15–60)

- [ ] Create the new key with the **smallest permissions** that work (for example a Stripe restricted key).
- [ ] Put it in `.env` on your machine and in the host's secret settings. Never in code.
- [ ] Redeploy, and check that the app works.

## 3. Check the damage (the same day)

- [ ] Look at the provider's logs and bills for the time the key was exposed.
- [ ] Look for things you did not create: users, servers, deployments, API calls, charges.
- [ ] If customer data may have been read, write down what, when and how many people. You may have legal duties to tell them; get advice.

## 4. Clean up (this week)

- [ ] Remove the key from the code.
- [ ] If it was committed, it is still in the git history, in every clone and in every fork. Only rewrite history after step 1. GitHub's guide: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- [ ] Make sure the file is in `.gitignore`, and that gitleaks runs on commit and push (the Build It Safe Kit's `doctor` checks both).

## 5. Learn (within two weeks)

- [ ] Write down in a few lines what happened, how you found out, and what you changed. No blame; just facts.
- [ ] Add one check that would have caught it sooner.

## Other emergencies

| What happened | First step |
|---|---|
| A package you installed was reported malicious | Rotate every credential on that machine (npm, GitHub, cloud, SSH, AI keys). Then remove the package. |
| Your framework announced a critical flaw | Patch the same day. If the app ran unpatched while exposed, rotate its secrets. |
| Strange charges | Treat it as a leaked key: step 1. Then set a hard spending cap. |
| An AI agent deleted data | Stop the agent. Stop all writes. Restore from a tested backup. Do not let the agent "repair" it. |
| You lost access to an account | Use the provider's recovery process and your saved recovery codes. Then review its connected apps and sessions. |

## Contacts

Fill these in before you need them:
- Hosting provider support: ______________________
- Payment provider support: ______________________
- Who else must be told: ______________________
