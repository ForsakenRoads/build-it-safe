## Installing the kit {#ch-kit}

::: {.dek}
The kit turns the most important rules in this book into settings and checks that run by themselves.
:::

### What the kit adds to a project

The companion kit lives in the same repository as this book, at `https://github.com/ForsakenRoads/build-it-safe`. It adds four layers to a project, all from one source [[kit-readme]]:

1. **The rules block** from {{ch:ch-agent-rules}}, in a marked block in `AGENTS.md` (for Codex, Cursor and Copilot), `CLAUDE.md` (for Claude Code) and `GEMINI.md` (for Gemini CLI).
2. **The secure-build skill:** longer reference pages on secrets, logins and data, dependencies, deploys, agents and tools, backups and incidents, in `.agents/skills/` and linked into `.claude/skills/`. The agent loads them only when a task needs them.
3. **A guard hook** for AI agents, `.build-it-safe/guard.py`. It refuses to read key files by any route it can see, including `cat`, `base64`, `cp` and short scripts. It refuses `rm -rf` on broad paths, force-pushing `main`, `git reset --hard`, dropping databases, `curl … | sh`, `--no-verify`, and writing a literal key into a file. The kit wires it into the hook settings of Claude Code, Codex, Cursor, Copilot and Gemini CLI, and adds Claude Code deny rules for key files.
4. **Checks:** gitleaks before every commit and every push, a check for hidden characters in agent rules files, and, for projects on GitHub, an automated workflow and Dependabot settings.

The installer never overwrites your files. It adds marked blocks, merges settings entry by entry, creates templates only when they are missing, and shows you its plan first. Running it twice changes nothing, and `uninstall` removes exactly what it added [[kit-readme]].

### Read this first: what the kit cannot do

Before you install anything, know how far to trust it. A row of green ticks from the doctor means the protections are in place. It does not mean your project is safe.

The guard stops the common ways an agent leaks a key or breaks something, and it keeps working when the agent's instructions are lost or hijacked. As of the kit's version of 16 October 2026, besides reading key files by name, it also stops [[kit-security; kit-support-matrix]]:

- downloaded code that reaches a shell or interpreter, at any step of a pipeline, or through `eval`, `source` or `xargs`;
- commands that dump all your environment variables, or print one whose name looks secret;
- `shred`, `truncate` on files outside build, log and temporary folders, and deleting your `main` branch.

It does **not** stop [[kit-security]]:

- a read that does not name the file, such as a search across a whole folder, or a script that walks a folder and opens what it finds;
- a shortcut (a "symlink") to a secret file that is already in the project;
- a `> file` redirect, which empties a file;
- an install script that already ran when a package was installed;
- every clever way to run code, such as a script downloaded in one step and run in a later one, or a command built in disguise;
- anything outside the agent's own actions, such as what you type yourself.

::: {.box .watch-out}
**Watch out**

The kit reduces common mistakes. It is a seatbelt, not a wall. For untrusted code, or for no-questions modes, run the agent in a sandbox or a container, with none of your keys inside ({{ch:ch-agent}}).
:::

The kit also cannot test your database rules, set your spending caps, choose your keys' permissions or restore your backups. Those are the chapters of Part II, and the checklists in {{ch:ch-checklists}}.

### You will need

- **git**, and the project you want to protect, already under git.
- **Python 3.8 or later**, which the installer, the doctor and the guard use.
- **gitleaks**, the secret scanner, for the commit and push checks. Without it, the hooks fall back to basic patterns [[kit-readme; gitleaks-repo]].
- A terminal: Terminal on macOS, or a Linux shell. On Windows, use WSL or Git Bash; native Windows is not supported [[kit-support-matrix]].

### Step 1: get the kit and see the plan

Download the kit next to your project, then go into your project and run the installer in "dry run" mode. It changes nothing; it only prints what it would do:

```
git clone https://github.com/ForsakenRoads/build-it-safe
cd my-app
python3 ../build-it-safe/tools/install --dry-run
```

Line by line: `git clone` downloads the kit into a folder called `build-it-safe`. `cd my-app` moves into your project; use your project's folder name. `python3` runs the installer with Python; `../build-it-safe/tools/install` is the installer, one folder up; `--dry-run` means "show the plan, change nothing".

![The installer's plan in a sample Next.js project: the agents and frameworks it found, and every file it would create. Nothing is written.](images/kit/install-dry-run.png)

Read the plan. Each line names a file and says why it is there. At the bottom, the installer prints an optional step for your own computer, explained below under "The one setting for your whole computer".

### Step 2: install

When the plan looks right, run it for real:

```
python3 ../build-it-safe/tools/install --yes
```

`--yes` means "apply the plan without asking again". Without it, the installer shows the plan and waits for you to type `y`.

![The same plan, applied, with the next steps.](images/kit/install.png)

Then commit the new files, so your teammates and your agents get the same protection. To remove the kit later, run `python3 ../build-it-safe/tools/install uninstall --yes`.

### Step 3: check with the doctor

The doctor reports what is in place, what is missing, and what to do next, in plain words. It only reads; it never opens your `.env` files:

```
python3 ../build-it-safe/tools/doctor
```

![The doctor's report in a sample project with two planted mistakes. A cross marks the committed `.env.local` file; an exclamation mark warns about a secret-looking name behind `NEXT_PUBLIC_`. The numbered steps at the end say what to do.](images/kit/doctor.png)

A tick means a protection is in place. A cross means something needs fixing, an exclamation mark is a warning, and an "i" is a note. The numbered steps at the end say what to do. Run the doctor again each month ({{ch:ch-checklists}}).

### Step 4: see it work

Two things now happen by themselves. When you, or your agent, try to commit or push a key, gitleaks stops it (see the figure in {{ch:ch-secrets}}). When an agent tries to read your `.env` file, the guard refuses (see the figure in {{ch:ch-agent}}). Either way, the message says why. Do not work around it: remove the key from the change, or give the agent the variable's name instead of its value.

### What the kit's own tests showed

The kit was tested live with Claude Code 2.1.300 on 16 October 2026, in fresh sample projects whose `.env` held a random test string, never a real key [[kit-support-matrix]]. Its offline test suite also checks the guard against 99 commands, the October 2026 review's attack examples among them, in the formats of all five agents; on 16 October 2026 all 62 tests passed, twice in a row [[kit-tests]]. The live results:

- **The guard still blocks in no-questions mode.** With `--dangerously-skip-permissions`, Claude Code still ran the project's guard hook, and the guard still blocked reading `.env` through the Read tool, `cat`, `base64` and a short Python script, and blocked `curl … | sh`.
- **Deny rules alone have a gap.** With only Claude Code's deny rules in place, reading `.env` with Read, `cat` and `base64` was blocked, but `python3 -c "print(open('.env').read())"` printed the file. Anthropic's documentation warns about exactly this: read rules do not cover "a Python or Node script that opens files itself" [[cc-permissions]]. That gap is why the kit adds the guard hook as a separate layer.
- **The rules did their part.** With the full kit installed, the agent refused to read `.env` without even trying, in both normal and no-questions mode. The guard is there for the times the rules are not enough.

### The one setting for your whole computer

A project's hooks protect you only when an agent runs inside that project. The Nx malware in {{ch:ch-installing}} started AI tools from the victim's home folder, where no project hooks exist [[kit-support-matrix]]. To stop anyone, or any malware, from starting Claude Code in its no-questions mode anywhere on your computer, add this to the file `~/.claude/settings.json` in your home folder [[cc-permission-modes]]:

```json
{
  "permissions": { "disableBypassPermissionsMode": "disable" }
}
```

Line by line: `permissions` is the section for permission settings. `"disableBypassPermissionsMode": "disable"` switches off the `--dangerously-skip-permissions` mode. If the file already has a `permissions` section, add the line inside it instead of adding a second section. The kit prints this advice, but it never edits your home folder; you make this change yourself. For a single project, the installer's `--lock-bypass` option sets the same switch in that project's settings [[kit-readme]].

### For Claude Code: the plugin

Claude Code users can also install the guard and the skill as a **plugin**, a package of add-ons for Claude Code, from the kit's own repository. Inside Claude Code, type:

```
/plugin marketplace add ForsakenRoads/build-it-safe
/plugin install build-it-safe@build-it-safe
```

The first line registers the kit's repository as a source of plugins. The second installs the plugin named `build-it-safe` from it. The names in square brackets are placeholders until the repository is published [[cc-discover-plugins]]. A plugin cannot add permission deny rules or git hooks, so for a project you share with others, prefer the installer, which commits the protection for everyone [[kit-readme]].
