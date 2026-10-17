# Secrets: keys, tokens and environment variables

A **secret** is any value that lets someone act as you: an API key, a database password, a token, a private key, a webhook signing secret. Whoever holds it can spend your money or read your data.

## Where secrets live

- **Local development:** in `.env` (or `.env.local`), which is listed in `.gitignore` and never committed. You, the agent, never open it.
- **Production:** in the host's secret store (Vercel, Netlify, Cloudflare, Fly, Render and others all have one), never in the repository.
- **Code:** reads the value from the environment, for example `process.env.STRIPE_SECRET_KEY` or `os.environ["STRIPE_SECRET_KEY"]`.
- **Documentation:** `.env.example` lists every variable name with a placeholder value. It is committed. Keep it up to date when you add a variable.

## The browser is public

Some frameworks copy variables with a special prefix into the JavaScript that every visitor downloads. Anyone can read them with the browser's built-in tools.

| Framework | Prefix that reaches the browser |
|---|---|
| Next.js | `NEXT_PUBLIC_` |
| Vite | `VITE_` |
| Create React App | `REACT_APP_` |
| Expo | `EXPO_PUBLIC_` |
| Nuxt | `NUXT_PUBLIC_` and `runtimeConfig.public` |
| SvelteKit 2 | `PUBLIC_` (`$env/static/public`) |
| SvelteKit 3 | variables marked `public: true` in `src/env.ts` |
| Astro | `PUBLIC_`, and `astro:env` with `access: "public"` |

Rules:
- Never put a secret key behind one of these prefixes, even "for now".
- Publishable keys are designed for the browser: Stripe `pk_…`, Supabase `sb_publishable_…`, a Firebase web API key restricted to Firebase services. Secret keys are not: Stripe `sk_…`/`rk_…`, Supabase `sb_secret_…` or `service_role`, any OpenAI, Anthropic or Gemini key.
- If the browser needs data that only a secret key can fetch, add a server route that holds the key and returns only what the page needs.
- A host marking a variable "secret" or "sensitive" does not protect a `NEXT_PUBLIC_` value: the framework still copies it into the bundle at build time.

Vercel's v0 reported blocking more than 17,000 deployments in 30 days because of secrets exposed this way (Vercel blog, 4 Aug 2025).

## Least privilege

- Use the narrowest key that works. Stripe recommends restricted keys (`rk_`) over secret keys for new uses, and lets you tag keys used by AI agents.
- Use separate keys for development and production, and separate projects or workspaces where the provider offers them (Anthropic workspaces, OpenAI projects).
- Prefer short-lived tokens with an expiry date (GitHub fine-grained tokens, npm granular tokens, OIDC publishing in CI).
- Set a hard spending cap where the provider offers one, and an alert where it does not. As of October 2026: OpenAI and Anthropic offer hard limits; AWS budgets and Google Cloud's ordinary budgets only alert.

## Git keeps everything

Every commit is a snapshot. Deleting a key in a new commit leaves it in every older commit, every clone and every fork. So:
- keep `.env` and key files in `.gitignore` before the first commit;
- let the gitleaks hook scan each commit and push; never bypass it;
- if a key was ever committed, treat it as leaked: see [incidents.md](incidents.md).

Attackers find leaked keys in minutes. In Clutch Security's test, AWS keys planted on GitHub were used after 6.6 minutes on average.

## What you do

- [ ] New variable: add the name to `.env.example` with a placeholder; read it from the environment in code; tell the human to set the real value in `.env` and in the host.
- [ ] Never print environment variables, `.env` content or keys in logs, errors, tests or your replies.
- [ ] No secret behind a public prefix. Move secret calls to a server route.
- [ ] Check `.gitignore` covers `.env`, `.env.*` (except `.env.example`), key files and local credential files.
- [ ] Never commit with `--no-verify`. If the scan reports a key, remove the key; if it is a false alarm, ask the human to allowlist it in `.gitleaks.toml`.

## Sources

- Next.js environment variables: https://nextjs.org/docs/app/guides/environment-variables
- Vite env and modes: https://vite.dev/guide/env-and-mode
- Expo environment variables: https://docs.expo.dev/guides/environment-variables/
- Nuxt runtime config: https://nuxt.com/docs/4.x/guide/going-further/runtime-config
- SvelteKit environment variables: https://svelte.dev/docs/kit/environment-variables
- Astro environment variables: https://docs.astro.build/en/guides/environment-variables/
- Supabase API keys: https://supabase.com/docs/guides/api/api-keys
- Stripe API keys: https://docs.stripe.com/keys and https://docs.stripe.com/keys-best-practices
- Vercel, "v0: vibe coding securely": https://vercel.com/blog/v0-vibe-coding-securely
- Clutch Security, leaked-key test (3 Dec 2024): https://www.clutch.security/blog/shattering-the-rotation-illusion-part-1-code-hosting-and-version-control-platforms
- OpenAI spend limits: https://developers.openai.com/api/docs/guides/spend-limits
- Anthropic rate and spend limits: https://platform.claude.com/docs/en/api/rate-limits
- Google Cloud budgets: https://docs.cloud.google.com/billing/docs/how-to/budgets
