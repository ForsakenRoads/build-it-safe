# .build-it-safe

This folder was added by the Build It Safe Kit. Commit it, so everyone who works on this repository, and every AI agent, gets the same protection.

- `guard.py`: the hook that AI agents run before each tool call. It blocks reading secret files, destructive commands, `curl | sh`, skipped git hooks and keys written into files.
- `hidden_text.py`: finds invisible characters in agent rules files.
- `git-hooks/`: the gitleaks checks that run before each commit and push.
- `config.json`: settings a human may change (protected branches, extra secret paths, protected function names). Agents are blocked from editing this folder.
- `manifest.json`: what the installer added, so `install uninstall` can remove exactly that.

Check the setup any time with the kit's `doctor`. Remove it with the kit's `install uninstall`.
