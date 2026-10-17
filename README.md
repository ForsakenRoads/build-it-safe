# Build It Safe

**Security for people who build with AI.** A project of Forsaken Roads® ([@Forsaken_Roads](https://x.com/Forsaken_Roads)).

Build It Safe is a project intended to improve safety and security for developers who use machine intelligence to code and release projects. Originally scoped and written by Claude Opus 5.5\*.

**Status:** private draft. Not published.

**[Read the manual (PDF)](manual/dist/security-primer.pdf)** · [EPUB](manual/dist/security-primer.epub)

## In 30 seconds

The Build It Safe Kit adds safety rails to any app you build with an AI coding assistant, so your AI can't leak your passwords, wipe your data or run a stranger's code. It installs with one command.

If you build apps with AI tools like Claude Code, Cursor or Copilot, the AI can make expensive mistakes. It can paste your passwords into your code, delete your database, or get tricked into running malware. This has happened to real people. The Build It Safe Kit is free, open-source safety equipment you add to your project with one command:
- **house rules** your AI reads every time it starts work;
- **a guard** that blocks dangerous actions before they happen, even if the AI was tricked;
- **a check** that stops passwords and keys from ever being uploaded to GitHub.

You keep working the same way; the kit only speaks up when it stops something. The free Build It Safe book explains why each rule exists.

```sh
git clone https://github.com/ForsakenRoads/build-it-safe
cd my-project
python3 ../build-it-safe/tools/install --yes      # or --dry-run first, to see the plan
python3 ../build-it-safe/tools/doctor
```

In Claude Code you can instead type `/plugin marketplace add ForsakenRoads/build-it-safe`, then `/plugin install build-it-safe@build-it-safe`.

## What kind of thing is this?

- It is an **open-source guardrails kit for AI coding assistants.** It is not an app with a screen, and not an MCP server: an MCP server gives an AI new abilities, while this kit limits what the AI may do.
- It installs **per project, as files inside the repository:** a rules block in `AGENTS.md` and `CLAUDE.md`; a skill; hook settings for each AI tool; a guard program in `.build-it-safe/`; git hooks; and, if you want, a GitHub workflow.
- So it works the same in VS Code with Copilot, in Cursor, in Claude Code (in the terminal or its VS Code extension), and with Codex and Gemini CLI. Everyone who clones the project gets the same protection.

| Tool | Rules file it reads | Skill folder it reads | Hook settings the guard runs from |
|---|---|---|---|
| Claude Code (terminal or VS Code extension) | `CLAUDE.md` (which imports `AGENTS.md` when the kit creates it) | `.claude/skills/` | `.claude/settings.json` |
| OpenAI Codex | `AGENTS.md` | `.agents/skills/` | `.codex/hooks.json` |
| Cursor | `AGENTS.md`, `.cursor/rules/` | `.agents/skills/` | `.cursor/hooks.json` |
| GitHub Copilot (VS Code agent mode, CLI, cloud agent) | `AGENTS.md`, `.github/copilot-instructions.md` | `.agents/skills/` | `.github/hooks/build-it-safe.json` (CLI and cloud agent; GitHub does not list VS Code as a hook runtime) |
| Gemini CLI | `GEMINI.md` | `.agents/skills/` | `.gemini/settings.json` |

The git hooks (gitleaks before every commit and push) work the same whatever tool you use. Details and sources: [kit/SUPPORT-MATRIX.md](kit/SUPPORT-MATRIX.md).

This repository holds two things:

1. **The manual,** a plain-language security primer for people who build software with AI tools, with no computer-science background needed. It tells the true stories of what went wrong, explains the few ideas that prevent most of it, and ends with checklists.
2. **The kit,** a drop-in for any repository that makes AI coding agents work safely there. It puts short security rules where each agent reads them, adds a full protocol the agent loads when the work needs it, and adds **guardrails written as code**: a hook that stops an agent from reading your keys, running destructive commands or switching off your checks, even when the agent has been tricked or told to skip its permission prompts.

## The official project, and forks

Open source means anyone can read, copy and change this project. It does **not** mean Forsaken Roads® endorses every copy.

- **Anyone can fork this project**, including people who may add malicious changes. The Build It Safe Kit runs code on your machine and tells your AI agent what to do, so a tampered copy can do real harm.
- **Forsaken Roads® reviews and supports only the official repository**, https://github.com/ForsakenRoads/build-it-safe, and the releases published there. Nothing else is endorsed, however similar it looks.
- **Every fork must say clearly that it is a fork,** and link to the original project. It must not use the Build It Safe or Forsaken Roads® names in a way that suggests it is official (see [TRADEMARKS.md](TRADEMARKS.md)).
- **Contributions to the official project go through the reviewed process only.** Anyone may propose a change; only vetted professionals who volunteer are given review or merge rights (see [GOVERNANCE.md](GOVERNANCE.md)).

**How to check you have the official version:**
1. It comes from the official repository address above, not a look-alike name or a re-upload.
2. It is listed on that repository's **Releases** page. (Signed release tags, shown with GitHub's **Verified** badge, are planned for later releases; release 0.1.0 is not signed.)
3. The files match the published checksums: download `SHA256SUMS` from the official release and run `sha256sum -c SHA256SUMS` (on macOS, `shasum -a 256 -c SHA256SUMS`). This covers the manual PDF and the release files.

If any of the three fails, do not install it. [SECURITY.md](SECURITY.md#verify-you-have-the-official-version) has the details.

## What the kit adds to your repository

| Layer | What it is | Where it goes |
|---|---|---|
| 1. Rules | About 20 lines of non-negotiables: never read `.env`, never put keys in code, check access on the server, ask before anything destructive … | A marked block in `AGENTS.md` (Codex, Cursor, Copilot), `CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini CLI) |
| 2. The protocol | The `secure-build` skill: secrets, auth and data, dependencies, deploys, agents and tools, backups, incidents. Loaded only when the work touches those subjects | `.agents/skills/secure-build/` (shared by Codex, Cursor, Copilot, Gemini CLI) and `.claude/skills/` |
| 3. Guardrails as code | A pre-tool-use **guard** that blocks: reading secret files when a tool or command names them (including through `cat`, `base64`, `cp` and `python -c`); dumping the environment (`printenv`, `env`, `set`, `echo $…_KEY`); downloaded code reaching a shell or interpreter anywhere in a pipeline (`curl … \| tee x \| sh`, `eval "$(curl …)"`); `rm -rf` on broad paths, `shred`, force-pushing or deleting `main`, `git reset --hard`, dropping databases; `--no-verify`; and writing a literal key into a file. Plus Claude Code deny rules. The exact list and the known limits are in [SECURITY.md](SECURITY.md#what-the-guard-blocks) | `.build-it-safe/guard.py`, wired into `.claude/settings.json`, `.cursor/hooks.json`, `.codex/hooks.json`, `.github/hooks/`, `.gemini/settings.json` |
| 4. Checks | gitleaks before every commit and push; a hidden-character check for agent rules files; a GitHub Actions workflow (gitleaks, hidden characters, dependency review); Dependabot | `.build-it-safe/git-hooks/`, `.github/workflows/build-it-safe.yml`, `.github/dependabot.yml` |

The installer never overwrites your files. Rules go in marked blocks, settings are merged entry by entry, and templates are created only when missing. JSON settings files (such as `.claude/settings.json`) are reformatted to standard two-space indentation when the kit merges its entries into them; your keys and values are kept. Running it twice changes nothing, and `uninstall` removes exactly what it added.

## Quick start (for humans)

You need `git`, Python 3.8 or later, and preferably [gitleaks](https://github.com/gitleaks/gitleaks#installing) (the hooks fall back to basic patterns without it).

```sh
# 1. Get the kit (anywhere on your computer)
git clone https://github.com/ForsakenRoads/build-it-safe

# 2. In your project, see what it would do. Nothing is written.
cd my-project
python3 ../build-it-safe/tools/install --dry-run

# 3. Install, then check
python3 ../build-it-safe/tools/install --yes
python3 ../build-it-safe/tools/doctor

# 4. Commit the new files so your team and your agents get them
git add -A && git commit -m "Add Build It Safe Kit"
```

Useful options: `--agents claude,cursor` (instead of detecting), `--with-ci`, `--with-templates` (adds `SECURITY.md` and `docs/security/`: incident playbook, launch checklist, backup protocol), `--lock-bypass`. To remove it: `python3 ../build-it-safe/tools/install uninstall --yes`.

## Quick start (for AI agents)

If you are an AI coding agent asked to set this up:
1. Run `python3 <kit>/tools/install --dry-run` in the project and show the human the plan.
2. Run it with `--yes` only after the human agrees.
3. Run `python3 <kit>/tools/doctor` and report every ✗ and its next step.
4. From then on, follow the rules block in `AGENTS.md` or `CLAUDE.md`, and load the `secure-build` skill for keys, logins, payments, databases, deploys, new packages, backups or a possible leak.

You cannot edit `.build-it-safe/` or remove the guard; that is by design. Ask the human.

## Claude Code plugin

The kit is also a Claude Code plugin (the guard hook plus the skill), with a marketplace in this repository:

```
/plugin marketplace add ForsakenRoads/build-it-safe
/plugin install build-it-safe@build-it-safe
```

A plugin cannot add permission deny rules or git hooks, so for a repository you share, prefer `tools/install`, which commits the protection for everyone.

## Support matrix

| Agent | Rules file it reads | Reads the skill | Guard hook | Tested |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md`, or `AGENTS.md` when there is no `CLAUDE.md` | yes (`.claude/skills/`) | `PreToolUse` + deny rules | **live, including `--dangerously-skip-permissions`** |
| Codex | `AGENTS.md` | yes (`.agents/skills/`) | `PreToolUse` (after you trust it in `/hooks`) | payload format |
| Cursor | `AGENTS.md`, `.cursor/rules` | yes (`.agents/skills/`) | `beforeShellExecution`, `beforeReadFile`, `preToolUse` | payload format |
| GitHub Copilot | `AGENTS.md`, `.github/copilot-instructions.md` | yes (`.agents/skills/`) | `.github/hooks/` (CLI, cloud agent) | payload format |
| Gemini CLI | `GEMINI.md` | yes (`.agents/skills/`) | `BeforeTool` | payload format |

Details, the live test results and every source: [kit/SUPPORT-MATRIX.md](kit/SUPPORT-MATRIX.md).

**Operating systems:** Linux (tested) and macOS (expected; the scripts avoid GNU-only flags). On Windows, use WSL or Git Bash.

**What the guard is not.** It is a seatbelt, not a wall: it stops the common ways an agent reads secrets or breaks things, and it keeps working after the agent's instructions are compacted or hijacked. It does not stop a search that reads files without naming them (`grep -r`), a symlink to a secret that already exists, a truncating `> file`, install scripts that already ran, or every disguised way to fetch and run code. The full list is under [Known limits](SECURITY.md#known-limits). For untrusted code or no-prompt modes, run the agent in a container or with Claude Code's sandbox.

## Repository layout

```
manual/            the primer (source, images, built PDF and EPUB)
kit/core/          the rules block
kit/skills/        the secure-build skill (Agent Skills format)
kit/guard/         the guard hook
kit/git-hooks/     pre-commit and pre-push (gitleaks)
kit/checks/        hidden-character check, ratchet recipe, protected-code guide
kit/agents/        hook and settings fragments for each agent
kit/ci/            GitHub Actions workflow, CodeQL note
kit/pre-commit/    config for the pre-commit framework
kit/templates/     .gitignore lines, .env.example, .gitleaks.toml, SECURITY.md, playbook, checklists, backup protocol
plugin/            the Claude Code plugin (built from kit/ by tools/build-plugin)
tools/             install, doctor, build-plugin
tests/             the test suite (sample repos, generated fake keys) and the live Claude Code test
```

## Contributing

This is moderated open source: every change is reviewed by a maintainer, and every factual claim needs a source. See [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md), [SECURITY.md](SECURITY.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## Licence

The code is under the [Apache License 2.0](LICENSE) (keep the [NOTICE](NOTICE) file); the manual is under [CC BY-ND 4.0](manual/LICENSE): share it freely, with credit, unchanged. Neither licence covers the Forsaken Roads® name ([TRADEMARKS.md](TRADEMARKS.md)). [LICENSING.md](LICENSING.md) explains both in plain words.

---

\*Claude Opus 5.5 is an AI model made by Anthropic. The research, writing and code were produced by Claude Opus 5.5 under the direction of Forsaken Roads®, then independently fact-checked and reviewed by Claude Fable 5.1. This project is not affiliated with or endorsed by Anthropic.
