## Your AI agent is a power tool {#ch-agent}

::: {.dek}
Rules you write are advice. Settings the tool enforces are locks. Use both.
:::

### The mental model: three layers of safety

A coding agent is a power tool. It saves you days of work. It can also cut through something you meant to keep, in seconds, without malice and without asking. A carpenter does not make a nail gun safe by asking it nicely. The safety comes from guards built into the tool and from how you set up the workshop.

An AI agent has three layers of safety, and they are not equally strong:

1. **Instructions:** the rules file the agent reads first, such as `CLAUDE.md` or `AGENTS.md`. These shape what the agent tries to do. Anthropic says plainly that Claude Code treats them "as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead" [[cc-memory]].
2. **Permissions and hooks:** settings that the agent's software enforces, whatever the AI decides. A deny rule or a hook blocks an action every time.
3. **Sandboxes and separate machines:** limits enforced by your operating system or a separate computer. The agent cannot reach what is not there.

Use all three. The rest of this chapter explains each one, then the two risks that make them necessary: prompt injection, and add-ons from strangers.

![Three layers of safety for an AI agent. Instructions guide it; permissions and hooks block actions; a sandbox or separate machine limits what it can reach.](images/diagrams/agent-layers.svg){width=92%}

### Permission modes, and the no-questions modes

Every major agent can either ask you before it acts or act on its own. As of October 2026, Claude Code starts interactive sessions in "auto mode", in which a second AI model, a classifier, approves or blocks each action instead of you [[cc-permission-modes]]. Anthropic writes that auto mode "reduces permission prompts but does not guarantee safety", and that a limit you state in chat "can be lost" when a long conversation is compacted. "For a hard guarantee, add a deny rule instead" [[cc-permission-modes]].

Every agent also has a mode that skips the questions entirely:

| Tool | No-questions mode | What the maker says |
|---|---|---|
| Claude Code | `--dangerously-skip-permissions` | "Only use this mode in isolated environments like containers, VMs, or dev containers without internet access" [[cc-permission-modes]] |
| OpenAI Codex | `--dangerously-bypass-approvals-and-sandbox` (`--yolo`) | "Only use inside an externally hardened environment" [[codex-cli-ref]] |
| Copilot in VS Code | `chat.tools.global.autoApprove` | "Bypasses all user approvals, potentially leading to destructive actions" [[vscode-copilot-security]] |
| Cursor | "Run Everything" | "Every tool call runs automatically" [[cursor-run-modes]] |

The Nx malware in {{ch:ch-installing}} used exactly these modes to turn its victims' AI tools into search programs [[snyk-nx]]. Treat these modes as you would treat removing the guard from a saw: only in a separate, disposable place, never on the computer that holds your keys.

### Deny rules and hooks: locks the agent cannot argue with

A **deny rule** tells the agent's software never to allow an action. In Claude Code, this is the official example for keeping an agent out of your key files [[cc-settings]]:

```json
{
  "permissions": {
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

Line by line: `permissions` is the section for permission settings. `deny` lists actions that are always refused. `Read(./.env)` means "reading the file named `.env` in this project". `Read(./.env.*)` covers files such as `.env.local` and `.env.production`.

Deny rules are strong, and they have edges. Anthropic's documentation says that Claude Code's read rules also apply to common shell commands such as `cat`, `head` and `tail`, but not to "a command that reads files without naming them, such as `grep -r pattern .`", or to "a Python or Node script that opens files itself". For that, it recommends the sandbox [[cc-permissions]]. The kit's live tests showed the gap: with deny rules alone, a one-line Python command printed a test `.env` file, while the guard hook blocked it, even in no-questions mode ({{ch:ch-kit}}).

A **hook** is a small program that the agent's software runs before every action. It can inspect the action and refuse it. Hooks can block patterns that are hard to express as rules, such as "a command that downloads a script and runs it". The kit that comes with this book installs a hook that refuses to read key files ({{ch:ch-kit}}).

![A real headless Claude Code run, asked to read `.env`. The agent tries `cat .env` in the shell; the kit's guard hook blocks it before the file is opened, and the agent turns to `.env.example` instead. (The agent chooses its own tool, so the attempt varies between runs.) For this capture the kit's rules block, skill and deny rules were removed, so only the guard stood in the way.](images/kit/guard-blocks-env-read.png)

### Sandboxes: limit what the agent can reach

A **sandbox** is a fence that your operating system enforces around a program. As of October 2026, Claude Code's sandbox is **off by default**. When on, it limits *writes* to your project and a temporary folder. But it lets commands *read* the whole computer by default, which "still allows reading credential files", unless you deny those paths. It covers shell commands only; Claude's own file tools, MCP servers and hooks run outside it [[cc-sandboxing]]. OpenAI's Codex, in a folder under version control, starts with writes limited to the workspace, approvals on request, and network access off [[codex-approvals]].

The strongest fence is a separate machine: a container, a virtual machine, or a cloud environment with no keys of yours inside. Even then, Anthropic warns that when Claude Code runs with `--dangerously-skip-permissions`, a dev container does not stop "a malicious project from exfiltrating anything accessible inside the container" [[cc-devcontainer]]. So put nothing valuable inside.

### No production keys within reach

The agents in {{ch:ch-replit}} and {{ch:ch-least-privilege}} did their damage with production access that happened to be within reach. So:

- Keep production keys out of the folder and the computer where your agent works.
- Give the agent development keys, a development database and read-only access wherever you can.
- Put a human between the agent and production: you deploy, after you have looked.

### Prompt injection: when text becomes orders

An agent reads text, and it can mistake text for orders. **Prompt injection** means hiding orders inside something the agent will read: a README, a GitHub issue, a web page, a code comment, or a tool's description. OWASP ranks it the number one risk for AI applications, and says "it is unclear if there are fool-proof methods of prevention" [[owasp-llm01]]. Anthropic writes that "no system is completely immune to all attacks" [[cc-security]].

This is not theory. In 2025 a researcher showed injected text making Claude Code read a `.env` file and send it out through internet address lookups, which were approved automatically. Anthropic's advisory describes "an overly broad allowlist of safe commands", fixed in version 1.0.4 [[cc-advisory-dns; embrace-claude-dns]]. Another attack made GitHub Copilot switch on its own no-questions mode by editing a settings file; Microsoft patched it in August 2025 [[embrace-copilot-yolo]]. In April 2026 a researcher showed that a pull-request title or an issue could make three AI bots on GitHub, from Anthropic, Google and GitHub itself, leak secrets where the attacker could read them. The vendors paid bug bounties; the researcher reports that not every fix is complete [[oddguan-comment-control]].

The researcher Simon Willison describes the dangerous combination as the **lethal trifecta**: an agent with access to your private data, exposure to untrusted content, and a way to send data out. His advice is never to give one agent all three at once [[willison-trifecta]].

Even opening a project can be an attack. In one Claude Code flaw, fixed in version 1.0.111, code in a project could run before you accepted the "do you trust this folder?" prompt [[cc-advisory-59536]]. Agent makers fix these flaws through updates, so keep auto-update on.

### MCP servers, skills and plugins from strangers

An **MCP server** is a plug-in that gives an agent new tools, such as access to GitHub, a database or email. A **skill** is a packaged set of instructions and files for a task. Both are software from someone else, with your agent's access.

- **Tool poisoning:** researchers showed a harmless-looking "add numbers" tool whose hidden description told the agent to read SSH keys and send them out [[invariant-tool-poisoning]].
- **A look-alike package:** in September 2025, an unofficial npm package named `postmark-mcp`, after a real email service, was reported to add a hidden copy of every outgoing email to an outside address [[snyk-postmark]]. The real company publishes its official server under its own name, `@activecampaign/postmark-mcp` [[postmark-official]].
- **Directories do not audit:** the official MCP Registry checks who owns a name but "delegates security scanning" to package registries [[mcp-registry]]. Anthropic reviews connectors for its directory "but does not security-audit or manage any MCP server" [[cc-security]].

Before you add one, check that it is the service's official server, read its tool list, give it the narrowest token you can, and keep approval prompts on. OWASP's advice: "Never auto-approve tool calls, especially in multi-server setups" [[owasp-mcp-cheatsheet]].

### Reviewing what the agent changed

You do not need to read code fluently to catch the most dangerous changes. Ask the agent for a summary of its changes, then look at the list of changed files (the **diff**). Stop and ask questions when you see:

- a long random-looking string, or a word like "key", "token" or "password" with a value next to it;
- a new package you did not ask for;
- changes to agent or editor settings (`.claude/`, `.cursor/`, `.vscode/`, `.mcp.json`) or to automated workflows (`.github/workflows/`);
- security switched off: tests deleted or skipped, `--insecure`, certificate checks disabled;
- a new web address, or a changed "base URL" for an API.

Do not take the agent's word for results. Replit's agent produced fake data and wrongly said a rollback was impossible ({{ch:ch-replit}}). Run the tests yourself and look at the data.

You can ask an AI for a security review, and it will find real problems. It will also report many false ones: in a test by the security company Semgrep, 86% of the vulnerabilities Claude Code reported and 82% of Codex's were false alarms, and repeated runs gave different results [[semgrep-ai-review]]. Use AI review as one more pair of eyes, next to scanners and your own tests, not as a verdict.

### Common AI-assistant mistakes

- Asking for broad permission ("allow all commands?") to save time.
- Editing its own settings, or the project's workflow files, to get past an obstacle.
- Reading `.env` "to understand the configuration".
- Installing an MCP server or package from a search result without checking who published it.

::: {.box .ask-agent}
**Ask your agent**

"Before you finish, list every file you changed, every package you added, every command you ran that changed something outside this folder, and every setting you changed. Flag anything that touches keys, permissions or deployment."
:::

::: {.box .do-this}
**Do this**

- Add deny rules for key files, and a guard hook, in every project ({{ch:ch-kit}}).
- Never use a no-questions mode on a computer that holds your keys, and switch it off for your whole computer if you can ({{ch:ch-kit}}).
- Keep production keys away from your agent's working folder and computer.
- Install MCP servers, skills and plugins only from their official publishers, and keep approvals on.
- Keep your agent tools updated, and review every diff before you deploy.
:::
