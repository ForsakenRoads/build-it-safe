# Auth and data: who may see what

**Authentication** answers "who is this?" (signing in). **Authorization** answers "may this person do this?" (permissions). Most data leaks in AI-built apps are authorization failures: the app knew who the user was, but never checked what they were allowed to see.

## Check on the server, every time

- Hiding a button or a page in the browser is not a lock. Anyone can call your API directly.
- Every API route, server action and database query that touches user data checks the session on the server, then checks that this user owns or may access the record.
- Do not rely on one checkpoint such as middleware alone. In March 2025 a Next.js flaw (CVE-2025-29927) let attackers skip middleware with one header on self-hosted apps. Check again where the data is read or changed.
- A record ID in a URL (`/invoices/123`) is not permission. Look up the record and confirm it belongs to the signed-in user.

## Supabase

- Turn on **Row Level Security (RLS)** on every table in an exposed schema, and write policies. Without RLS, a table "is readable and writable by any role with a grant on it". Tables created in the dashboard get RLS by default; tables created in SQL do not.
- With RLS on and no policies, the publishable key can read nothing. Add policies for exactly what each user may do, for example `auth.uid() = user_id`.
- The secret key (`sb_secret_…`, or the legacy `service_role` JWT) bypasses every RLS policy. It stays on the server only.
- Run the Security Advisor in the dashboard; it flags tables without RLS.
- As of 30 Oct 2026, new tables in `public` are no longer granted to the API roles automatically. Grants are a separate layer from RLS: you still need RLS.

Lovable's CVE-2025-48757 (2025) and Escape's scan of 5,600 vibe-coded apps (Oct 2025) both traced data exposure to tokens in front-end code combined with missing or wrong RLS.

## Firebase

- Security Rules are "the only safeguard blocking access for malicious users".
- "Test mode" rules let anyone read and overwrite the data. Never ship them, and never just extend their expiry date.
- `allow read, write: if true` lets "anyone who guesses your project ID" steal or delete data. `auth != null` alone lets every signed-in user read everyone's data.
- Write owner-only rules such as `request.auth.uid == resource.data.owner_uid`, and test them with the Emulator or the Rules Simulator.

## Other stacks

The same rules apply to any database: the server checks the user and the ownership of each record; queries use parameters, never glued-together strings; the database user the app connects with has only the rights it needs.

## Payments and webhooks

- Payment amounts and what the user bought are decided on the server, never taken from the browser.
- Verify every webhook's signature with the provider's library and the endpoint's signing secret. For Stripe: check the `Stripe-Signature` header with `constructEvent`, using the **raw** request body. Never set the timestamp tolerance to 0.
- Treat an unverified webhook as a forgery: "an attacker could send fake webhook events to your endpoint to trigger actions like fulfilling orders".

## Input and output

- Check every input for the expected type, format and length on the server.
- Use parameterized queries or the ORM's query builder. Never build SQL from user text.
- Escape user content before showing it in HTML. Avoid `dangerouslySetInnerHTML` and its equivalents with user content.

## What you do

- [ ] Every new route or server action checks the session and the record's owner.
- [ ] Every new table has RLS on (or rules written) with a policy, in the same change that creates it.
- [ ] Test as a stranger (signed out) and as a second user: neither may see the first user's data. Tell the human how you tested, or that you could not.
- [ ] No secret database key in front-end code.
- [ ] Webhooks verify signatures on the raw body.

## Sources

- Supabase Row Level Security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase API keys: https://supabase.com/docs/guides/api/api-keys
- Supabase Data API grants change: https://github.com/orgs/supabase/discussions/45329
- Firebase Security Rules basics: https://firebase.google.com/docs/rules/basics and insecure rules: https://firebase.google.com/docs/rules/insecure-rules
- Next.js middleware bypass, CVE-2025-29927: https://nextjs.org/blog/cve-2025-29927
- Escape, vibe-coded apps study: https://escape.tech/blog/methodology-how-we-discovered-vulnerabilities-apps-built-with-vibe-coding/
- CVE-2025-48757 (Lovable): https://nvd.nist.gov/vuln/detail/CVE-2025-48757
- Stripe webhooks: https://docs.stripe.com/webhooks
- OWASP Top 10:2025 (A01 Broken Access Control): https://top10.owasp.org/2025
