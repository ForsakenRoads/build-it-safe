# Kit screenshots for the manual

Every image is a capture of a REAL run in a sample repository, made by `tests/screenshots.py`: the real command runs, its colour output is converted to HTML and photographed with headless Google Chrome. Fake keys are generated at run time and redacted by gitleaks. The only edit is that the sample folder's absolute path is shown as `~/projects/my-app`, and the push remote as `github.com:you/my-app.git`.

| File | What it shows | Size (px) | Captured |
|---|---|---|---|
| `gitleaks-push-blocked.png` | `git push` stopped by the kit's pre-push hook: gitleaks found an AWS access key in a commit made before the kit was installed. The key is generated for the demo and shown as REDACTED. | 901 × 506 | 17 Oct 2026 |
| `guard-blocks-env-read.png` | A real headless Claude Code run (`claude -p`, Claude Code 2.1.300) asked to read `.env`. The kit's PreToolUse guard blocks the agent's attempt before the file is opened (the tool call it tried is shown; the agent picks the tool, so it varies between runs), and the agent reports the block. Shown as a transcript of the run's event stream. For this capture the rules block, the skill and the deny rules were removed so that only the guard stood in the way (with them in place, the agent declines before trying). | 901 × 706 | 17 Oct 2026 |
| `install-dry-run.png` | `tools/install --dry-run` in a sample Next.js project: the agents and frameworks it found, and its plan. Nothing is written. | 901 × 686 | 17 Oct 2026 |
| `install.png` | `tools/install --yes` in the same project: the same plan, applied, and the next steps. | 901 × 726 | 17 Oct 2026 |
| `doctor.png` | `tools/doctor` after installing the kit in a project with two mistakes: a committed `.env.local` and a secret-looking name behind `NEXT_PUBLIC_`. Ticks, crosses and the next steps. | 901 × 826 | 17 Oct 2026 |
