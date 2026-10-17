## Secrets {#ch-secrets}

::: {.dek}
The browser is public. Your server is private. Keys belong on the server.
:::

### The mental model: two places your code runs

A web app runs in two places. Part of it runs on your **server**: a computer you rent from a host such as Vercel, Netlify or Cloudflare. Nobody but you can read what is on it. The other part runs in the **browser** of every person who visits your site. To run it there, the browser downloads it. Whatever the browser downloads, the visitor can read, with tools built into every browser.

So there is one rule, and most of this chapter follows from it: **anything sent to the browser is public.** A key in browser code is a key you have handed to every visitor.

![Two places your code runs. Settings with a public prefix are copied into the code every visitor downloads; everything else stays on the server.](images/diagrams/browser-vs-server.svg){width=95%}

::: {.box .plain-words}
**Plain words**

- **Secret:** anything that grants access. API keys, passwords, database connection strings (a database address with a password inside it), signing keys and tokens.
- **API key:** a password that lets a program use a paid service. Whoever holds it can spend your money or read your data.
- **Environment variable:** a named setting, such as `OPENAI_API_KEY`, that your app reads when it starts. It keeps the value out of your code.
:::

### The public prefixes

Most frameworks have a way to send a setting to the browser on purpose. They do it with a prefix on the variable's name. The prefix sounds harmless. It is really an instruction: "copy this value into the code that every visitor downloads." Next.js, for example, says such a value "will be inlined into any JavaScript sent to the browser" [[nextjs-env]].

As of October 2026:

| Framework | What makes a variable public | What the docs say |
|---|---|---|
| Next.js | `NEXT_PUBLIC_` | "inlined into any JavaScript sent to the browser" [[nextjs-env]] |
| Vite | `VITE_` | "should *not* contain sensitive information such as API keys" [[vite-env]] |
| Expo (mobile apps) | `EXPO_PUBLIC_` | "visible in plain-text in your compiled application" [[expo-env]] |
| Create React App (deprecated in 2025) | `REACT_APP_` | "Do not store any secrets (such as private API keys) in your React app!" [[cra-env; react-sunset-cra]] |
| Nuxt | `runtimeConfig.public`, `NUXT_PUBLIC_` | added to each page sent to the browser [[nuxt-runtime]] |
| SvelteKit 2 | `PUBLIC_` (the default `publicPrefix`) | "safe to expose to client-side code" [[sveltekit2-config]]; this module is deprecated in SvelteKit 3 [[sveltekit-public]] |
| SvelteKit 3 | `public: true` in `src/env.ts` | every variable is private unless marked public [[sveltekit-env]] |
| Astro | `PUBLIC_` | "Secret client variables are not supported" [[astro-env]] |

Some keys are designed to be public, and that is fine. Supabase's **publishable** key (`sb_publishable_…`) and Stripe's **publishable** key (`pk_…`) are meant for browsers [[supabase-api-keys; stripe-keys]]. They are safe only because the service checks every request with other rules: Supabase with row-level security ({{ch:ch-doors}}), Stripe by allowing very little with that key. A secret key next to them (`sb_secret_…`, `sk_…`) must never reach a browser.

Hosting a secret on a good host does not change this rule. Vercel's Secret type hides a value from your team, but if its name starts with `NEXT_PUBLIC_`, Next.js still copies it into the browser code when it builds the site [[nextjs-env; vercel-secret-vars]].

![A demo page built for this book. The right side shows the JavaScript file the browser downloaded. The fake secret key from a `NEXT_PUBLIC_` variable sits in it as plain text, where any visitor can read it.](images/web/next-public-key-in-browser.png)

### Where keys live

- **On your computer,** keys go in a file named `.env` (or `.env.local`) in your project. Your framework reads it when you run the app.
- **On your host,** keys go in the host's secret settings: Vercel's Secret variables, Netlify's secret variables, Cloudflare's `wrangler secret put` [[vercel-secret-vars; netlify-secrets; cloudflare-secrets]]. Cloudflare's advice applies everywhere: "Do not use plaintext environment variables to store sensitive information" [[cloudflare-secrets]].
- **In your code,** keys never appear. The code names the variable, and the value comes from outside.
- **In a template,** you can share the *names* without the values. A file called `.env.example` lists every variable your app needs, with fake values, so the next person knows what to set.

### `.gitignore`, and why history is forever

**Git** is the tool that saves versions of your project, and **GitHub** is a website that stores them. A file called `.gitignore` lists files that git must never save. Your `.env` files belong in it:

```
.env
.env.*
!.env.example
```

Line by line: the first line ignores the file named `.env`. The second ignores every file whose name starts with `.env.`, such as `.env.local`. The third line, starting with `!`, makes an exception, so the harmless template is still saved.

`.gitignore` only stops *new* files. If git already saved a key, ignoring the file now does not remove it. Git keeps every version you ever saved. Deleting a file in a new version leaves it in every older one, and in every copy anyone made. GitHub's own guide says that when a secret is committed, "as a first step you need to revoke and/or rotate that secret" [[github-remove-sensitive]]. Removing it from history is slow and cannot reach copies that already exist ({{ch:ch-leak}}).

### Scanners: a second pair of eyes

A **secret scanner** reads your changes and stops you when it sees something that looks like a key.

- **GitHub push protection** is on by default for your pushes to public repositories. It blocks known key formats [[github-push-protection]]. For private repositories on personal accounts, GitHub does not alert you about secrets [[github-secret-scanning]], so run a scanner on your own computer.
- **gitleaks** is a free, open-source scanner (MIT license) that runs before each commit or push [[gitleaks-repo]]. Its maintainer says it is now "feature complete", receives security fixes only, and that his new work goes into a successor called Betterleaks [[gitleaks-repo]]. gitleaks still works, and this book's kit uses it. One trap: the kit's own tests found that gitleaks 8.30.1 reported no leaks at all when git was set to always print colour (`color.ui=always`), so the kit's hooks switch colour off when they run it [[kit-tests]].
- **TruffleHog** can scan a project's whole history and check whether a found key still works [[trufflehog-repo]].

![The kit's pre-push hook stops a push: gitleaks finds a key, generated for this demo, in a commit made before the kit was installed, and shows it as REDACTED.](images/kit/gitleaks-push-blocked.png)

Some providers also watch for their own keys. Supabase revokes its secret keys when it finds them in public GitHub repositories [[supabase-retro-2025]]. Stripe may deactivate an exposed key itself [[stripe-keys-best]]. Do not count on it. Clutch's test in {{ch:ch-published-keys}} showed attackers acting within minutes.

### Common AI-assistant mistakes

- Putting a secret in a public variable "so the front end can call the API". The fix is a small server route that calls the API for the browser.
- Writing a key straight into the code "just for testing". Test code gets committed too.
- Printing keys in logs or error messages while debugging.
- Creating `.env` without adding it to `.gitignore`.
- Asking you to paste a key into the chat. Paste it into your `.env` file yourself instead.

::: {.box .ask-agent}
**Ask your agent**

"List every environment variable this project uses. For each, tell me whether it reaches the browser, and why. Flag any secret that has a public prefix or is written in the code. Do not print any values."
:::

::: {.box .do-this}
**Do this**

- Search your project for public prefixes (`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`, `PUBLIC_`). Move every secret you find to the server.
- Add `.env` and `.env.*` to `.gitignore`, and keep a `.env.example` with fake values.
- Store production keys in your host's secret settings, marked secret.
- Install a secret scanner that runs before every commit and push ({{ch:ch-kit}}).
- Keep a list of every key: what it is for, where it is stored, and how to rotate it.
:::
