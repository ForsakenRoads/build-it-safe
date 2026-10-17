# Fact log (writer, round 1, 16 Oct 2026)

How to trace a claim: every `[[key]]` in `manual/src/*.md` resolves to one line in `manual/src/95-sources.md`.
The PDF numbers sources in order of first citation. This log records (A) what the writer verified directly,
with the URL and date, (B) where the writer's check CORRECTED a research file, and (C) what came from the
research files without a fresh check, with their confidence labels.

All checks: 16 Oct 2026, by WebFetch or WebSearch, or by reading the primary file (restic docs and changelog
fetched from the restic GitHub repository; Cure53 PDF read as text).

## A. Verified directly by the writer

| Chapter | Claim (short) | Source key | URL |
|---|---|---|---|
| 1 | EnrichLead posts of 15 and 17 Mar 2025, exact wording incl. "not technical", "ever since I started to share" | cendyne-vibe | https://cendyne.dev/posts/2025-03-19-vibe-coding-vs-reality.html |
| 1 | Firebase: deployed app "publicly accessible — even if you haven't launched it" | firebase-rules-basics | https://firebase.google.com/docs/rules/basics (quote from FUNDAMENTALS, page is primary) |
| 2 | Moltbook: title, author, date 2 Feb 2026; 1.5M tokens, 35,000 emails, 4,060 DMs, 17,000 owners; contact 31 Jan 21:48 UTC, first fix 23:29, final 1 Feb 01:00; RLS sentence | wiz-moltbook | https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys |
| 2 | Lovable: discovery 20 Mar 2025, CVE published 29 May 2025, data types | palmer-cve | https://mattpalmer.io/posts/2025/05/CVE-2025-48757/ |
| 2 | "303 endpoints across 170 projects (approximately 10.3% of the 1645 analyzed)"; scan "checks for the existence of any RLS policy, not its correctness" | palmer-statement | https://mattpalmer.io/posts/2025/05/statement-on-CVE-2025-48757/ |
| 2 | Escape: 5,600+ apps, ~4,000 Lovable, 2,000+ vulns, 400+ secrets, 175 PII, quotes, passive scan = lower bound | escape-method | https://escape.tech/blog/methodology-how-we-discovered-vulnerabilities-apps-built-with-vibe-coding/ |
| 3 | v0: 17k in 30 days, 100k since launch, top keys, 1,000+ Supabase, 1,000 AI keys, NEXT_PUBLIC_ quotes | vercel-v0-secure | https://vercel.com/blog/v0-vibe-coding-securely |
| 3 | Clutch: 6.6 min average, 1-30 min, AWS alert 1.4 min | clutch-rotation | https://www.clutch.security/blog/shattering-the-rotation-illusion-part-1-code-hosting-and-version-control-platforms |
| 3 | Sysdig: LLMjacking, ten services, "$46,000 … per day" | sysdig-llmjacking | https://www.sysdig.com/blog/llmjacking-stolen-cloud-credentials-used-in-new-ai-attack |
| 3 | Microsoft Storm-2139: four named, "exploited exposed customer credentials scraped from public sources" | ms-storm2139 | https://blogs.microsoft.com/on-the-issues/2025/02/27/disrupting-cybercrime-abusing-gen-ai/ |
| 3 | GitGuardian 2026: 28,649,024 (+34%), AI 1,275,105 (+81%), Claude Code "~2× the baseline" (correlation stated in text) | gitguardian-2026 | https://www.gitguardian.com/state-of-secrets-sprawl-report-2026 |
| 4 | Register: quotes "eleven times in ALL CAPS", fake data, 4,000 records, rollback "impossible"/"did work", $607.70 | register-replit | https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/ |
| 4 | Fortune: "more than 1,200 executives", "over 1,190 companies"; Masad quotes and fixes | fortune-replit | https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/ |
| 5 | Vercel bulletin: origin, takeover, "enumerate and decrypt…", scope, npm, recommendations, closed (updated 16 Oct 2026) | vercel-april-bulletin | https://vercel.com/kb/bulletin/vercel-april-2026-security-incident |
| 5 | Context.ai "Allow All", March AWS access, Hudson Rock Lumma / Roblox quote | thn-vercel-context | https://thehackernews.com/2026/04/vercel-breach-tied-to-context-ai-hack.html |
| 5 | ShinyHunters Telegram claim; GTIG "likely an imposter…" | cyberscoop-vercel | https://cyberscoop.com/vercel-security-breach-third-party-attack-context-ai-lumma-stealer/ |
| 6 | Nx: "active for 4 hours…", root cause (PR title in workflow) | nx-postmortem | https://nx.dev/blog/s1ngularity-postmortem |
| 6 | Wiz s1ngularity figures | wiz-s1ngularity | https://www.wiz.io/blog/s1ngularity-supply-chain-attack |
| 6 | Snyk: exact AI CLI flags; prompt begins "You are a file-search agent." | snyk-nx | https://snyk.io/blog/weaponizing-ai-coding-agents-for-malware-in-the-nx-malicious-package/ |
| 6 | CISA: "over 500 packages"; "Immediately rotate all developer credentials" | cisa-shai-hulud | https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem |
| 6 | Shai-Hulud 2.0 hit Zapier, PostHog, Postman packages | wiz-shai-hulud-2 | https://www.wiz.io/blog/shai-hulud-2-0-ongoing-supply-chain-attack |
| 6, 13 | PostHog root cause; switched to pnpm 10 to disable install scripts and use minimumReleaseAge | posthog-shai-hulud | https://posthog.com/blog/nov-24-shai-hulud-attack-post-mortem |
| 6 | react-codeshift: 47 skills, 237 repos, registered by Aikido | aikido-slopsquatting | https://www.aikido.dev/blog/slopsquatting-ai-package-hallucination-attacks |
| 6 | AWS-2025-015: token, syntax error, 1.84.0 / 1.85.0, CVE-2025-8217 | aws-q-bulletin | https://aws.amazon.com/security/security-bulletins/AWS-2025-015/ |
| 6 | CSO wording "behave like a system cleaner…" | cso-amazon-q | https://www.csoonline.com/article/4027963/hacker-inserts-destructive-code-in-amazon-q-as-update-goes-live.html |
| 7 | React advisory quotes, CVSS 10.0 | react-advisory | https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components |
| 7 | Vercel: versions 15.0.0-16.0.6, `npx fix-react2shell-next`, rotate advice with the 4 Dec 1:00 PM PT time | vercel-react2shell | https://vercel.com/kb/bulletin/react2shell |
| 8 | Censys: 21,639 on 31 Jan 2026; "~1,000 to over 21,000 in under a week"; most "still require a token" | censys-openclaw | https://censys.com/blog/openclaw-in-the-wild-mapping-the-public-exposure-of-a-viral-ai-assistant/ |
| 8 | O'Reilly's report (labelled unconfirmed in text) | trending-openclaw | https://www.trendingtopics.eu/clawbot-hyped-ai-agent-risks-leaking-personal-data-security-experts-warn/ |
| 8 | ClawHub: 341 of 2,857 skills, 335 AMOS | thn-clawhub | https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html |
| 8, 17 | OpenClaw: "loopback-only" quote, `ssh -N -L 18789:127.0.0.1:18789`, "the safest default (no public exposure)" | openclaw-remote | https://docs.openclaw.ai/gateway/remote |
| 10 | Firebase test mode: "Good for getting started … allows anyone to read and overwrite your data" | firebase-quickstart | https://firebase.google.com/docs/firestore/quickstart |
| 10 | Supabase grants change: 28 Apr / 30 May / 30 Oct 2026; existing tables keep grants; separate from RLS | supabase-grants-change | https://github.com/orgs/supabase/discussions/45329 |
| 9, 10 | Supabase retro: auto-revokes leaked secret keys; RLS on by default for dashboard tables | supabase-retro-2025 | https://supabase.com/blog/supabase-security-2025-retro |
| 9 | Stripe may deactivate exposed keys proactively | stripe-keys-best | https://docs.stripe.com/keys-best-practices |
| 11 | PocketOS: staging, token "scoped for any operation, including destructive ones", "9 seconds", backups in same volume, restored | register-pocketos | https://www.theregister.com/software/2026/04/27/cursor-opus-agent-snuffs-out-startups-production-database/5224442 |
| 11 | Railway: API volume deletes soft-delete for 48 hours, 1 May 2026 | railway-undoable-deletes | https://railway.com/changelog/2026-05-01-undoable-deletes |
| 12 | OpenAI: alerts "API traffic continues", "Enforce a hard limit", "Enforcement is not instantaneous" | openai-spend-limits | https://developers.openai.com/api/docs/guides/spend-limits |
| 12 | Google spend caps: covered services, pause behavior, "isn't instant … billed as normal" | gcp-spend-caps | https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps |
| 12 | Gemini: "~10 minute delay", users responsible for overages; tier caps | google-gemini-costs | https://blog.google/innovation-and-ai/technology/developers-tools/more-control-over-gemini-api-costs/ |
| 12 | Vercel Spend Management (updated 18 Sep 2026): not a stop on its own; Pause Production Deployments; checks every few minutes; does not stop AI Gateway or v0 | vercel-spend | https://vercel.com/docs/spend-management |
| 12 | Supabase Spend Cap (Pro): usage disallowed past quota until next cycle | supabase-cost-control | https://supabase.com/docs/guides/platform/cost-control |
| 12 | AWS Free account plan: "You will not incur any charges during this period…", up to six months | aws-free-plan | https://docs.aws.amazon.com/en_us/awsaccountbilling/latest/aboutv2/free-tier.html |
| 13 | `npm ci` exits with an error instead of updating the lock | npm-ci | https://docs.npmjs.com/cli/v11/commands/npm-ci |
| 13 | npm: `min-release-age` (days), `allow-scripts`, `strict-allow-scripts` (default warns), `ignore-scripts` | npm-config | https://docs.npmjs.com/cli/v11/using-npm/config |
| 13 | pnpm: `minimumReleaseAge` minutes, default 1440 since v11, added 10.16.0; "within an hour" quote | pnpm-resolution | https://pnpm.io/settings/dependency-resolution |
| 13 | pnpm: packages not in `allowBuilds` "are disallowed by default" | pnpm-build | https://pnpm.io/settings/build |
| 13 | `npm audit fix --force` can install SemVer-major changes | npm-audit | https://docs.npmjs.com/cli/v11/commands/npm-audit |
| 13 | OpenSSF concise guide checks | openssf-concise | https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software |
| 14 | Claude Code: auto mode default from v2.1.283; "does not guarantee safety"; "For a hard guarantee, add a deny rule instead"; bypass mode "Only use this mode in isolated environments…" | cc-permission-modes | https://code.claude.com/docs/en/permission-modes |
| 14 | Claude Code read deny rules cover cat/head/tail…, not `grep -r` or scripts; sandbox for OS-level enforcement | cc-permissions | https://code.claude.com/docs/en/permissions |
| 14, 21 | "as context, not enforced configuration … use a PreToolUse hook instead"; AGENTS.md read in place of CLAUDE.md | cc-memory | https://code.claude.com/docs/en/memory |
| 14 | Codex `--yolo`: "Only use inside an externally hardened environment" | codex-cli-ref | https://learn.chatgpt.com/docs/developer-commands?surface=cli |
| 14 | Codex defaults: workspace write + on-request approvals; network off by default | codex-approvals | https://learn.chatgpt.com/docs/agent-approvals-security |
| 14 | VS Code `chat.tools.global.autoApprove` warning | vscode-copilot-security | https://code.visualstudio.com/docs/copilot/security |
| 14 | Cursor "Run Everything": "Every tool call runs automatically" | cursor-run-modes | https://cursor.com/docs/agent/security/run-modes |
| 14 | CVE-2025-55284 advisory: "overly broad allowlist of safe commands", fixed v1.0.4 | cc-advisory-dns | https://github.com/anthropics/claude-code/security/advisories/GHSA-x5gv-jw7f-j6xj |
| 14 | Rehberger: `.env` via DNS (`ping` auto-approved), fixed v1.0.4 | embrace-claude-dns | https://embracethered.com/blog/posts/2025/claude-code-exfiltration-via-dns-requests/ |
| 14 | Copilot YOLO via `.vscode/settings.json`; fixed August 2025 Patch Tuesday | embrace-copilot-yolo | https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/ |
| 14 | Comment and Control: three bots; bounties; not every fix complete | oddguan-comment-control | https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot/ |
| 14 | CVE-2025-59536: code ran before the trust dialog; fixed v1.0.111 | cc-advisory-59536 | https://github.com/anthropics/claude-code/security/advisories/GHSA-4fgq-fpq9-mr3g |
| 14 | postmark-mcp: hidden BCC reported (1.0.16 alleged) | snyk-postmark | https://snyk.io/blog/malicious-mcp-server-on-npm-postmark-mcp-harvests-emails/ |
| 14 | Official server `@activecampaign/postmark-mcp` | postmark-official | https://github.com/activecampaign/postmark-mcp |
| 14 | MCP Registry: namespace verification; "delegates security scanning"; in preview | mcp-registry | https://modelcontextprotocol.io/registry/about |
| 14 | Semgrep: 86% / 82% false positives; 3, 6, 11 findings | semgrep-ai-review | https://semgrep.dev/blog/2025/finding-vulnerabilities-in-modern-web-apps-using-claude-code-and-openai-codex/ |
| 15 | CISA: FIDO/WebAuthn "the only widely available phishing-resistant authentication" (page is archived; said so in Sources) | cisa-mfa | https://www.cisa.gov/MFA |
| 15 | Google linked apps page and steps | google-linked-apps | https://support.google.com/accounts/answer/13533235 |
| 15 | GitHub Authorized OAuth Apps steps | github-oauth-review | https://docs.github.com/en/apps/oauth-apps/using-oauth-apps/reviewing-your-authorized-oauth-apps |
| 15 | Repojacking, >100 clones retirement, bypass, 4,000+ packages, fixed | checkmarx-repojacking | https://checkmarx.com/blog/persistent-threat-new-exploit-puts-thousands-of-github-repositories-and-millions-of-users-at-risk/ |
| 15 | npm classic tokens disabled 5 Nov 2025; write granular tokens 2FA by default; 90-day cap | npm-classic-disabled | https://github.blog/changelog/2025-11-05-npm-security-update-classic-token-creation-disabled-and-granular-token-changes/ |
| 15 | Classic tokens revoked (changelog title, 9 Dec 2025) | npm-classic-revoked | https://github.blog/changelog/2025-12-09-npm-classic-tokens-revoked-session-based-auth-and-cli-token-management-now-available/ |
| 15 | Trusted publishing: "always prefer it over long-lived tokens" | npm-trusted-publishing | https://docs.npmjs.com/trusted-publishers |
| 16 | 3-2-1 definition | backblaze-321 | https://www.backblaze.com/blog/the-3-2-1-backup-strategy/ |
| 16 | B2 app keys: one bucket; capability list incl. `deleteFiles`, `bypassGovernance`; master key shown once | b2-app-keys | https://www.backblaze.com/docs/cloud-storage-application-keys |
| 16 | `b2 key create [--bucket] keyName capabilities` | b2-key-create | https://b2-command-line-tool.readthedocs.io/en/master/subcommands/key_create.html |
| 16 | Lifecycle: hiding, `daysFromHidingToDeleting`, hidden files still stored | b2-lifecycle | https://www.backblaze.com/docs/cloud-storage-lifecycle-rules |
| 16 | Object Lock: quote, governance vs compliance, cannot be turned off, no extra cost | b2-object-lock | https://www.backblaze.com/docs/cloud-storage-object-lock |
| 16 | restic: AES-256-CTR + Poly1305-AES | restic-design | https://github.com/restic/restic/blob/master/doc/design.rst |
| 16 | restic 0.19.1 (5 Jul 2026) latest; hide-only B2 keys = enhancement #2134 in 0.15.0 (12 Jan 2023), quotes | restic-changelog | https://github.com/restic/restic/blob/master/CHANGELOG.md |
| 16 | "Losing your password means that your data is irrecoverably lost"; app key "will only appear once"; S3 API recommended for B2 | restic-prepare | https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html |
| 16 | `key passwd`; `--exclude-caches`; `check --read-data-subset=n/t`; `forget --keep-tag` | restic-encryption, restic-backup, restic-working, restic-forget | restic docs (see Sources) |
| 17 | EFF: provider sees traffic; "not a tool for anonymity"; HTTPS protects content not metadata; "isn't as necessary for everyone anymore" (last reviewed 28 Jul 2026) | eff-vpn | https://ssd.eff.org/module/choosing-vpn-thats-right-you |
| 17 | WireGuard description | wireguard-home | https://www.wireguard.com/ |
| 17 | Cure53 Mullvad relay infrastructure, June 2024, "generally in exemplary condition", no remote-exploitable findings | cure53-mullvad-2024 | https://cure53.de/pentest-report_mullvad_2024_v1.pdf |
| 17 | Mullvad web app audit by Assured, 23 Oct 2025, no critical/high/medium | mullvad-assured-2025 | https://mullvad.net/en/blog/independent-security-audit-of-our-web-app-completed-by-assured |
| 17 | Mullvad raid 18 Apr 2023; left without data | mullvad-raid-2023 | https://mullvad.net/en/blog/2023/4/20/mullvad-vpn-was-subject-to-a-search-warrant-customer-data-not-compromised/ |
| 17 | Mullvad app GPL-3.0 | mullvad-app-repo | https://github.com/mullvad/mullvadvpn-app |
| 17 | Mullvad owned by founders via Amagicom AB; Gothenburg | mullvad-about | https://mullvad.net/en/about |
| 17 | "All of our VPN servers run from RAM, with no persistent storage" | mullvad-servers | https://mullvad.net/en/help/server-list |
| 17 | OpenVPN removed; servers off by 15 Jan 2026 | mullvad-openvpn-removal | https://mullvad.net/en/blog/removing-openvpn-from-the-mullvad-vpn-app |
| 17 | €5/month; account number; cash and crypto | mullvad-pricing | https://mullvad.net/en/pricing |
| 17 | Proton: Securitum audits 2022-2026; "tested in over 400 legal cases" (labelled Proton's figure); open-source apps | proton-nologs-audit | https://protonvpn.com/blog/no-logs-audit |
| 17 | Proton moving physical infrastructure; "not performing a gradual exit from Switzerland" | cyberinsider-proton-swiss | https://cyberinsider.com/proton-confirms-gradual-exit-from-switzerland-over-surveillance-law-fears |
| 17 | Proton Foundation "primary shareholder" (17 Jun 2024) | proton-foundation | https://proton.me/blog/proton-non-profit-foundation |
| 17 | Proton disks with LUKS, keys off-site; argues RAM-only adds nothing | proton-ram-only | https://protonvpn.com/blog/ram-only-servers |
| 17 | Proton offers WireGuard; Stealth (obfuscated TLS) | proton-wireguard, proton-stealth | see Sources |
| 17 | Proton pricing: VPN Plus $3.49/mo on 2-year; free plan; payment methods incl. credits for cash/Bitcoin | proton-pricing | https://protonvpn.com/pricing |
| 17 | ssh `-L`, `-N` | openssh-manual | https://man.openbsd.org/ssh.1 |
| 17 | Tailscale "peer-to-peer mesh network", WireGuard | tailscale-what | https://tailscale.com/kb/1151/what-is-tailscale |
| 18 | Let's Encrypt; MDN HSTS, CSP, frame-ancestors, nosniff; Observatory description; moved 2 Jul 2024; scan history public | letsencrypt-about, mdn-* | see Sources |
| 21 | AGENTS.md: steward and supporting tools | agents-md | https://agents.md/ |
| 21 | Copilot instruction files incl. AGENTS.md, CLAUDE.md, GEMINI.md | gh-copilot-instructions | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| 21 | Cursor `.cursor/rules`; supports AGENTS.md | cursor-rules | https://cursor.com/docs/context/rules |
| 21 | Yan preprint: 481 files; 4-16%, 4.4% | yan-claudemd | https://arxiv.org/abs/2608.23550 |
| 21 | Kit core block text (v1) quoted from the kit worktree, `kit/core/security-block.md`, as of 16 Oct 2026 | (internal) | — |

## B. Corrections to the research files

1. **restic version for no-delete B2 keys.** BACKUP-AND-VPN.md §B1 says hiding instead of deleting "needs version 0.17 or later". The restic changelog puts enhancement #2134 in **0.15.0** (12 Jan 2023). The book says 0.15.0 or later, and recommends the current 0.19.1.
2. **restic and B2: S3 API recommended.** restic's docs now recommend B2's S3-compatible API over the native `b2:` backend. The book's protocol stays backend-neutral; noted for the kit's BACKUP-PROTOCOL.md.
3. **Comment and Control.** AGENT-RISKS.md says "All three patched". The researcher's page says Anthropic added a partial block, Gemini paid a bounty with no patch described, GitHub "actively exploring". The book says the vendors paid bounties and not every fix is complete.
4. **postmark-mcp.** Snyk reports the 1.0.16 BCC as alleged by community reports; the code it shows is from 1.0.18. The book says "was reported to add".
5. **Amazon Q prompt wording.** The quote in INCIDENTS.md ("to clear a system to a near-factory state…") is not in the CSO article. The book uses CSO's own wording.
6. **Gemini project spend caps** are not called "experimental" in Google's 16 Mar 2026 post. Removed that word.
7. **Proton Stealth** is not WireGuard-based (Proton built it "from the ground up"; obfuscated TLS over TCP).
8. **PocketOS token.** The Register says the token was "scoped for any operation, including destructive ones", not "account-wide". The book uses The Register's words.
9. **Vercel attacker claims.** CyberScoop does not mention the $2 million price or ShinyHunters' denial. The book uses only what CyberScoop says (Telegram claim; Google analyst: "likely an imposter").
10. **React2Shell firewall figures** (6 million attempts; $1 million to researchers) are not in Vercel's bulletin. Left out.
11. **AWS Free plan date** ("accounts created from 15 July 2025") is not on the AWS page. Left out.
12. **Nx flags.** Nx's post-mortem does not list the AI CLI flags; Snyk's analysis does, and is cited for them.
13. **Mullvad's latest audits.** The March 2026 ranking cited an August 2025 Assured audit; Mullvad's blog dates the Assured web-app audit 23 Oct 2025. The infrastructure audit cited is Cure53's of June 2024 (read in full).
14. **OVPN** (third in the March 2026 ranking): its press page now names "OVPN Inc., incorporated in US" as the operating entity, and no published independent audit was found. Not presented as meeting the bar; left out of the book rather than named negatively.

## C. Taken from the research files without a fresh fetch (labels kept)

- **INCIDENTS.md:** Moltbook builder quote origin (social post quoted by Wiz: VERIFIED-PRIMARY for Wiz's quoting); Lemkin's and Masad's X posts (UNVERIFIED-SOCIAL, widely reported; the book says they are his own account); X post URLs; Wiz React2Shell figures and GreyNoise timing (VERIFIED-PRIMARY); Microsoft React2Shell figures (VERIFIED-PRIMARY); Spracklen figures (VERIFIED-PRIMARY); Next.js middleware CVE (VERIFIED-PRIMARY).
- **FUNDAMENTALS.md:** framework prefix table and quotes; Vercel Config/Secret types; Netlify, Cloudflare quotes; Supabase key types and RLS quotes; Firebase rules quotes; Stripe key types, RAK quote (wording date [UNVERIFIED], not dated in the book), rotation 7 days, webhook quote; Anthropic tier caps and workspaces; Google budgets alerts-only; AWS budgets; GitHub push protection and secret scanning; gitleaks "feature complete"; GitHub removing-sensitive-data guide; OWASP Top 10:2025 (A01, A03); AWS IAM quotes.
- **AGENT-RISKS.md:** Willison's lethal trifecta; OWASP LLM01 quote; Anthropic "no system is completely immune"; sandbox details (off by default, reads whole machine, "still allows reading credential files", file tools outside); dev-container quote; Claude Code settings deny example; Invariant tool poisoning; OWASP MCP cheat-sheet quote; Railway changelog (re-checked); OpenSSF AI guide and RCI.

## D. Round 2 (16 Oct 2026): fact-check fixes and kit alignment

All 30 FIX rows of `orders/FACTCHECK-1.md` applied (see `orders/READY-WRITER-2.md` for the list). New or re-checked facts:

| Claim | Source key | Checked |
|---|---|---|
| Context.ai's linked statement returns 404 | context-statement | https://context.ai/security-update (WebFetch: HTTP 404) |
| SvelteKit 2 `publicPrefix` default `PUBLIC_`, "safe to expose to client-side code" | sveltekit2-config | `@sveltejs/kit@2.70.3/types/index.d.ts` via unpkg |
| Dependabot security updates open pull requests | gh-dependabot-updates | GitHub Docs; the page does not state plan pricing, so the book says only that alerts are on every plan [gh-advanced-security] |
| Proton sign-up asks for an email (existing or a new @proton.me); a $2.99 two-year offer shown | proton-signup | live page rendered in headless Chrome (no account created) |
| X41 D-Sec API review, 20 Jan 2026: five findings, "high security level"; Mullvad: none give access to user data | x41-mullvad-2026, mullvad-x41-2026 | primary pages |
| Assured GotaTun audit, 6 Mar 2026: "no major vulnerabilities" | mullvad-gotatun-audit | Mullvad blog |
| GitGuardian +34% | thn-gitguardian-2026 | contributed article on The Hacker News (rounded "29 million … 34%") |
| AGENTS.md read by Codex; Gemini reads GEMINI.md, AGENTS.md via `context.fileName` | codex-agents-md, gemini-md | primary docs |
| Agent Skills folders for Claude Code, Codex, Cursor, Copilot, Gemini CLI | cc-skills, codex-skills, cursor-skills, gh-agent-skills, gemini-skills | primary docs |
| Claude Code reads AGENTS.md only with no CLAUDE.md; `@AGENTS.md` import | cc-memory | primary docs |
| Live kit results, Nx home-folder caveat, guard limits | kit-support-matrix | the kit's own test record (internal to the repository) |
| gitleaks 8.30.1 finds nothing with `color.ui=always` | kit-tests | the kit's regression test; no outside source found, so the book attributes it to the kit's tests |
| Plugin commands | cc-discover-plugins, kit-readme | Claude Code docs; kit README |

Removed: `mullvad-assured-2025` (the table now cites the newer X41 and GotaTun audits).

## E. Round 3 (16 Oct 2026): Fable items 6-8, re-shot screenshots

| Claim | Source key | Checked |
|---|---|---|
| What the guard now blocks (fetch-and-run through any pipeline stage, eval/source/xargs; environment dumps and secret-variable printing; shred, truncate outside build/log/temp, deleting `main`) | kit-security, kit-support-matrix | kit `SECURITY.md` and `kit/SUPPORT-MATRIX.md` at kit HEAD dd0f434 |
| What it does not stop (unnamed reads, existing symlink, `> file`, install scripts that ran, download-then-run and disguised commands, actions outside the agent) | kit-security | `SECURITY.md` "Known limits"; the kit builder checked each against the guard |
| 99 commands in each agent format; 62 tests passed twice on 16 Oct 2026 | kit-tests | kit test suite and its run log |
| Screenshot content and captions | — | each of the five re-shot PNGs viewed; captions rewritten for the guard (`cat .env` via the shell) and the doctor (one cross, one warning) |

## F. Round 4 (16 Oct 2026): the owner's decisions

"Why this exists" was rewritten from existing, already-checked sources only: cendyne-vibe, x-enrichlead-shutdown, wiz-moltbook, register-replit (Lemkin's exact words), x-masad-replit, vercel-april-bulletin, thn-vercel-context (the "Allow All" claim is attributed to Context.ai), snyk-nx and clutch-rotation. No new sources were added. The byline, handle and attribution come from the owner's decisions and live in `build/book.toml`.
