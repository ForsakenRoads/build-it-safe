# Screenshots and figures the manual needs

Rules: only our own captures, or pages we build. No vendor screenshots. Every example key is obviously fake
(for example `sk_live_EXAMPLE_NOT_REAL`). Terminal captures come from real runs of the real tools in sample repos.

Until a file exists at the path below, the build inserts a dashed **SCREENSHOT PLACEHOLDER** box with the
caption and the file name, and adds "(Placeholder: the screenshot is still to come.)" to the caption.
Drop the file in with exactly this name and rebuild (`python3 manual/build/build.py`); nothing else changes.

Recommended size for terminal captures: about 1000-1200 px wide, at most about 700 px tall, light background,
text at least 14 px, so it stays readable at 6.5 in wide in print.

## Screenshots

| File (under `manual/`) | What it must show | Chapter | Who | Status |
|---|---|---|---|---|
| `images/web/next-public-key-in-browser.png` | A page built for this book whose `app.js` contains an obviously fake secret from a `NEXT_PUBLIC_` variable, highlighted. Source: `images/web/demo/` | 9, Secrets | writer | DONE (headless Chrome capture of our demo page, 16 Oct 2026) |
| `images/kit/gitleaks-push-blocked.png` | gitleaks (through the kit's pre-push or pre-commit hook) refusing a push or commit that contains a fake, generated key. The key in the image must be redacted or obviously fake | 9, Secrets (referenced again in 22) | kit builder | DONE (real run, copied from the kit branch, 16 Oct 2026) |
| `images/kit/guard-blocks-env-read.png` | The kit's PreToolUse guard refusing an AI agent's attempt to read `.env` (for example a headless Claude Code run in a sample repo), with the guard's message visible | 14, Your AI agent (referenced again in 22) | kit builder | DONE (real run, copied from the kit branch, 16 Oct 2026) |
| `images/kit/install-dry-run.png` | `python3 tools/install --target <sample repo> --dry-run`: the printed plan (files it would write, agents it detected) | 22, Installing the kit | kit builder | DONE (real run, copied from the kit branch, 16 Oct 2026) |
| `images/kit/install.png` | `python3 tools/install --target <sample repo>`: the real install output | 22, Installing the kit | kit builder | DONE (real run, copied from the kit branch, 16 Oct 2026) |
| `images/kit/doctor.png` | `python3 tools/doctor --target <sample repo>`: ticks and crosses with the "next step" lines | 22, Installing the kit | kit builder | DONE (real run, copied from the kit branch, 16 Oct 2026) |

All five kit captures arrived with matching names; their provenance is in `images/kit/INDEX.md`. No placeholders remain.

## Diagrams (our own SVG, drawn for the book)

| File | Shows | Chapter | Status |
|---|---|---|---|
| `images/diagrams/browser-vs-server.svg` | Server versus browser; public prefixes copy values out | 9 | DONE |
| `images/diagrams/doors-and-locks.svg` | Authentication versus authorization, both on the server | 10 | DONE |
| `images/diagrams/scoped-keys.svg` | Master key versus scoped keys | 11 | DONE |
| `images/diagrams/agent-layers.svg` | Instructions, permissions and hooks, sandbox | 14 | DONE |
| `images/diagrams/backup-protocol.svg` | Encrypt, no-delete key, hidden versions kept, restore drill | 16 | DONE |
| `images/diagrams/remote-access.svg` | Exposed dashboard versus SSH tunnel or mesh VPN | 17 | DONE |
| `images/diagrams/leak-playbook.svg` | Revoke, replace, investigate, clean up | 19 | DONE |

## Considered and dropped

- A header check of a demo site in Mozilla's HTTP Observatory (chapter 18): it needs a public site, which would
  mean publishing. Dropped; the chapter describes the tool instead.
- Vendor dashboards (spend caps, B2 application keys, Vercel secret variables): not captured, by rule. The text
  describes them, and the diagrams cover the ideas.
