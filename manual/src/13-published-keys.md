## Keys you published without knowing it {#ch-published-keys}

::: {.dek}
A key in public code is found in minutes and spent like cash.
:::

### What happened

**Seventeen thousand in a month.** Vercel is a company that hosts websites, and v0 is its AI tool that builds them. In August 2025 Vercel reported that "in the past 30 days, v0 blocked over 17k deployments on Vercel due to exposed secrets alone". Since launch, v0 had blocked "over 100k insecure deployments" [[vercel-v0-secure]]. A deployment is one published version of a website.

The keys it caught most often were for Google Maps, reCAPTCHA, EmailJS and PostHog. "Over a thousand people almost handed over the keys to their app by sharing their Supabase backend and database keys", and "a thousand more were ready to share their OpenAI, Gemini, Claude, and xAI keys" [[vercel-v0-secure]]. Those are paid AI services.

**Six and a half minutes.** In a test it published in December 2024, the security company Clutch Security planted working AWS keys in public code on GitHub to see how fast attackers would find them. AWS is Amazon's cloud service, and its keys can rent computers by the hour. On GitHub, "on average, keys were exploited in 6.6 minutes from the time of exposure". The fastest took 1 minute; the slowest took 30 [[clutch-rotation]].

**Forty-six thousand dollars a day.** Attackers want AI keys in particular. In May 2024 the security company Sysdig named a new kind of attack "LLMjacking": criminals use stolen cloud credentials to run expensive AI models on the victim's account. In the case Sysdig studied, the attackers' script tested the stolen credentials against ten AI services, including Anthropic, AWS Bedrock, OpenAI and Google's Vertex AI. Sysdig estimated: "If undiscovered, this type of attack could result in over $46,000 of LLM consumption costs per day for the victim" [[sysdig-llmjacking]].

In February 2025 Microsoft named four developers in a group it calls Storm-2139. Microsoft says the group "exploited exposed customer credentials scraped from public sources", switched off the AI services' safety limits, and resold the access to people who made harmful images [[ms-storm2139]].

**The trend.** GitGuardian, a company that scans public code for secrets, counted 28,649,024 new secrets on public GitHub in 2025, a rise of 34% on the year before. Secrets for AI services rose 81%, to 1,275,105 [[gitguardian-2026; thn-gitguardian-2026]]. GitGuardian also reports that commits co-written with Claude Code "leak secrets at ~2× the baseline" [[gitguardian-2026]]. That is a correlation. It does not show that the tool causes the leaks; the projects may differ in other ways. It does show that AI-assisted code needs the same secret checks as any other code.

### Why it happened, in plain words

::: {.box .plain-words}
**Plain words**

- **Secret:** anything that grants access: an API key, a password, a database address with a password in it, a private token.
- **Environment variable:** a named setting, such as `OPENAI_API_KEY`, that your app reads when it runs. It keeps the value out of your code.
- **`NEXT_PUBLIC_`:** a prefix in Next.js, a popular web framework. Any variable whose name starts with it is copied into the code that every visitor's browser downloads.
:::

Vercel names one of the most common mistakes: "In Next.js, any environment variable prefixed with `NEXT_PUBLIC_` gets exposed to the browser." AI models "misuse this by placing secrets, like database credentials and API keys, into these public variables" [[vercel-v0-secure]]. The prefix sounds like a setting. It is really a publishing instruction.

Attackers do not search by hand. Programs scan public code and public websites around the clock, test every key they find, and use the ones that work. Clutch's numbers show how little time you have once a key is public. AWS's own warning arrived, on average, after 1.4 minutes [[clutch-rotation]], which is fast, and still not fast enough for a key you have not yet revoked.

::: {.box .lesson}
**The lesson**

- A public prefix (`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_` and others) means "published to the world". Put only truly public values there ({{ch:ch-secrets}}).
- Keep AI and payment keys on the server, and set a hard spending cap on each one ({{ch:ch-money}}).
- If a key was ever public, even for a minute, revoke it and make a new one. Deleting the file is not enough ({{ch:ch-leak}}).
:::
