## Doors and locks {#ch-doors}

::: {.dek}
Logging in proves who you are. It does not decide what you may touch.
:::

### The mental model: the ID check and the room keys

Think of a hotel. At the front desk, the clerk checks your ID. That is **authentication**: proving who you are. Then the clerk gives you a key card that opens one room. That is **authorization**: deciding what you may do. A hotel that checks IDs but gives every guest a master key has authentication and no authorization.

Many data leaks in apps built with AI, including those in {{ch:ch-open-database}}, are authorization failures. The app knows who you are. It just never asks whether *this* user may see *this* record. OWASP, the best-known open project on web security, ranks "Broken Access Control" as the number one risk in its 2025 list [[owasp-top10-2025]].

![Authentication checks who you are. Authorization checks what you may open. Both must happen on the server.](images/diagrams/doors-and-locks.svg){width=90%}

### Every check happens on the server

A check in the browser is a sign on the door, not a lock. The visitor controls the browser. They can skip a page, edit a button, or send requests straight to your server without using your pages at all. So:

- Hide buttons in the browser if you like, for a tidy screen. But check every action again **on the server**, at the moment it reads or changes data.
- Check in more than one place. In March 2025, Next.js disclosed that login checks placed only in its "middleware" layer could be skipped by sending one special header (CVE-2025-29927). Only self-hosted apps were affected [[nextjs-middleware-advisory; vercel-middleware-postmortem]]. Apps that checked again where they read data were still protected.
- A paywall is an authorization check too. Check that the user has paid on the server, every time.

### Databases that browsers talk to directly

Supabase and Firebase let the browser talk to the database directly. That is convenient, and it means the database itself must check every request. There is no server of yours in between.

**Supabase.** The database's lock is **row-level security** (RLS): rules that decide which rows each user may read or change. Supabase's documentation is blunt: "A table in an exposed schema without RLS is readable and writable by any role with a grant on it" [[supabase-rls]]. In plain words: a table without RLS is open to the world. Some facts to know, as of October 2026:

- RLS is switched on automatically for tables you create in the Supabase dashboard. It is *not* switched on for tables you create with SQL commands, such as the ones an AI assistant writes for you [[supabase-retro-2025]].
- With RLS on and no policies, the browser key sees nothing [[supabase-rls]]. You then write a policy for each kind of access, such as "a user may read their own profile".
- The **secret** key bypasses "every Row Level Security policy you have" [[supabase-api-keys]]. It belongs on a server only.
- From 30 October 2026, Supabase stops automatically opening *new* tables to the browser roles in every project. Existing tables keep their settings. Supabase notes that this layer is separate from RLS, so you still need RLS [[supabase-grants-change]].
- The Security Advisor in the Supabase dashboard flags every table in the public schema that has RLS switched off [[supabase-advisors]].

**Firebase.** The lock is **Security Rules**. Google calls them "the only safeguard blocking access for malicious users" [[firebase-rules-basics]]. Two patterns are traps:

- `allow read, write: if true;` means "anyone who guesses your project ID can steal, modify, or delete the data" [[firebase-insecure-rules]].
- `allow read, write: if request.auth != null;` lets *any* logged-in user read *all* the data [[firebase-insecure-rules]]. Anyone can sign up, so this is barely better.

When you start a database, Firebase offers "test mode". Google's own description: "Good for getting started … but allows anyone to read and overwrite your data" [[firebase-quickstart]]. Replace it with real rules before anyone else can find your app. A safe rule names the owner: a user may read a record only if the record's owner ID matches their own [[firebase-insecure-rules]].

### Webhooks are doors too

A **webhook** is a web address on your server that another service calls to tell you something happened, such as "this customer paid". Anyone can call that address. Stripe warns that "without verification, an attacker could send fake webhook events to your endpoint to trigger actions like fulfilling orders, granting account access" [[stripe-webhooks]]. Use the provider's official library to check the signature on every webhook before you act on it.

### Test as a stranger, then as a second user

You cannot see a missing lock by looking at a working app. You have to try the door. Two tests catch most mistakes:

1. **The stranger test.** Log out, or open a private browser window. Try every page and every action. Anything you can still see or change, a stranger can too.
2. **The second-user test.** Create two accounts, A and B. As A, create some data. As B, try to see it, change it and delete it, including by changing an ID in the web address. If B can touch A's data, your authorization is broken. Palmer's scan of the Lovable apps was the first test: he sent requests without logging in ({{ch:ch-open-database}}).

### Common AI-assistant mistakes

- Creating tables with SQL and never enabling RLS.
- Writing a policy that checks only "is logged in" instead of "owns this row".
- Using the Supabase secret key, or Firebase's admin access, in browser code "to fix a permission error". It fixes the error by removing the lock.
- Checking permissions in the page, not on the server.
- Skipping the webhook signature check "for now".

::: {.box .ask-agent}
**Ask your agent**

"For every table and every API route, tell me who can read it and who can change it, as a logged-out visitor, as a logged-in user, and as the owner. Show me where on the server each check happens. Do not change anything yet."
:::

::: {.box .do-this}
**Do this**

- Turn on RLS (Supabase) or write security rules (Firebase) for every table or collection, and give each one an owner-only policy.
- Make sure no secret or admin key appears in browser code.
- Check permissions and payment status on the server, where the data is read or changed.
- Verify every webhook's signature with the provider's library.
- Run the stranger test and the second-user test before launch, and after every big change.
:::
