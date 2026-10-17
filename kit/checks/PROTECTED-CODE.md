# Protected code: names an agent must not delete

Agents sometimes "simplify" code by deleting the part that mattered, such as replacing a permission check with `return true`. The guard can stop an edit that removes a function or variable you list.

## How to use it

A human adds entries to `.build-it-safe/config.json` (agents are blocked from editing that file):

```json
{
  "protected": [
    { "file": "src/auth/*.ts", "names": ["verifySession", "requireAdmin"] },
    { "file": "app/api/*/route.ts", "names": ["getServerSession"] }
  ]
}
```

- `file` is a shell-style pattern relative to the repository root (`*` also matches across folders, so `src/auth/*.ts` covers subfolders too).
- `names` are matched as whole words, case-sensitive.
- The guard blocks a Write or Edit to a matching file when the change leaves **fewer** occurrences of a listed name than before.

The kit always protects its own hook entries in `.claude/settings.json`, `.cursor/hooks.json`, `.codex/hooks.json`, `.gemini/settings.json`, `.github/hooks/` and `.github/workflows/build-it-safe.yml`, so an agent cannot quietly switch the guard off.

## Its limits

- It sees names, not meaning. A function emptied to a stub still contains its name and passes. Keep tests for the behaviour that matters.
- It guards the agent's file tools. Shell commands that rewrite your files (`sed -i`, scripts) are not compared. The guard does block any shell command that changes `.build-it-safe/`, the git hooks or the hook settings files listed above.
- Keep the list short: the few checks that protect money, data or access.
