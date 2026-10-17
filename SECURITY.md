# Security policy

## Reporting a vulnerability

Please do **not** open a public issue for a security problem in the kit (for example a way around the guard, a flaw in the installer, or a CI weakness) or a dangerous error in the manual. A public issue tells attackers before a fix exists.

Report it privately through GitHub: open the **Security** tab of this repository and choose **Report a vulnerability** (private vulnerability reporting). Or email **security@forsakenroads.com**. If neither works for you, send a direct message to [@Forsaken_Roads](https://x.com/Forsaken_Roads) on X, and we will open a private channel with you.

Please include:
- what you found and where;
- how to reproduce it;
- what an attacker could do with it.

Never include real keys or other people's data in a report.

We aim to acknowledge reports within 7 days, to agree a disclosure date with you, and to credit you in the release notes unless you prefer otherwise.

## Verify you have the official version

Anyone can fork this project, and a fork can carry malicious changes. Forsaken Roads® supports only the official repository and the releases published there. Before you install the kit or trust the manual:

1. **The official repository:** https://github.com/ForsakenRoads/build-it-safe. Check the address character by character; look-alike names and re-uploads are not official.
2. **The Releases page:** official releases are published only on the repository's Releases page. Signed release tags (GitHub's **Verified** badge; `git tag -v <tag>` from a clone) are planned for later releases; release 0.1.0 is not signed.
3. **Checksums:** each official release publishes a `SHA256SUMS` file covering the manual PDF and the release files. Run `sha256sum -c SHA256SUMS` (on macOS, `shasum -a 256 -c SHA256SUMS`); every line must say `OK`.

If any check fails, do not install it, and tell us privately (see above). Checksums start with release 0.1.0; signed tags will follow.

## Scope

In scope: everything in this repository, including the guard's ability to block what it claims to block. A command that does one of the things below and gets through is a bug; please report it.

## What the guard blocks

The guard (`kit/guard/guard.py`) checks each tool call an AI agent makes, before it runs. It blocks:

1. **Reading secret files**: `.env` and `.env.*` (not `.env.example`, `.env.sample` or `.env.template`), private keys, certificates, cloud and git credentials, npm and yarn client config (`.npmrc`, `.yarnrc`, `.yarnrc.yml`), database client passwords (`.pgpass`, `.my.cnf`), and `/proc/<pid>/environ` in any spelling. Paths are normalised (`/proc/./self/environ`, `//proc/self/environ`, `..`) and bash `$'...'` quotes are decoded before the name is checked. A backup suffix (`.bak`, `.old`, `.orig`, a trailing `~`) does not hide the name; a sample suffix (`.pem.example`) still does. By a file tool, or by a shell command that names the file (`cat`, `less`, `head`, `cp`, `mv` of a secret source, `base64`, `source`, `xargs`, `$(…)`, globs such as `.e*`, `< .env`, `python -c`, `node -e`), or by `git add`. Searching for the text `.env` (`grep .env README.md`) or mentioning it in a sentence is not a read.
2. **Environment dumps**: bare `printenv`, `env` with no command (`env`, `env | grep …`, `env -0`), bare `set`, `export -p` (with or without a secret name), `declare -p`/`-x`, `typeset -x`, `compgen -e` and `compgen -v`, PowerShell `Get-ChildItem env:`; printing a secret-looking variable (`printenv OPENAI_API_KEY`, `echo $…KEY`, `$…TOKEN`, `$…SECRET`, `$…PASSWORD`, `$…PASS`, `$…CREDENTIAL`, `$…PRIVATE`, `$DATABASE_URL`); and interpreter code that prints the whole environment or one secret (`os.environ`, `process.env`, `process["env"]`, Perl `%ENV`). A name is secret when a component is `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `PASS` or `CREDENTIAL`, not when those letters merely sit inside another word. `PATH`, `MAX_TOKENS`, `PUBLIC_KEY`, `CACHE_KEY` and `PRIVATE_IP` are not secrets. `export -p PATH` and `os.environ["PATH"]` stay allowed.
3. **Downloaded code reaching a shell or interpreter**: a `curl`, `wget`, `fetch`, `aria2c`, `iwr`/`Invoke-WebRequest` or similar whose output reaches `sh`, `bash`, `python`, `node`, `php`, `bun`, `iex` and the like **anywhere** later in the pipeline, including across a newline and inside `sh -c '…'`, through filters such as `tee`, `cat`, `head`, `tr`, `sed`, `grep`, `base64 -d`, `gunzip` or `xxd -r`, and through `tee >(php)` or `tee >(bun)`; `xargs`/`parallel` running a shell on fetched input; `eval`, `source` or `.` of a download (`eval "$(curl …)"`, `source <(curl …)`); `sh -c "$(curl …)"`, `bash <(curl …)`; a variable that captured a download and is then executed (`s=$(curl …); sh -c "$s"`); and a file downloaded and executed in the same command (`curl -o x.sh URL && sh x.sh`).
4. **Destruction**: `rm -r` on `/`, `~`, `.`, `*`, `.git`, the project root, shallow absolute paths, or a personal or credential folder directly under home (`~/Documents`, `~/.ssh`, `~/.config`, `~/.local`); `find … -delete` and `find … -exec rm` on those (a narrowed cleanup such as `find . -name '*.pyc' -delete` is allowed; `find ~ -name x -delete` and `find / -delete` are not); force-pushing, deleting or mirror-pushing `main`/`master`, including `git push --force origin HEAD` while that branch is checked out; `git branch -d/-D main`; `git update-ref -d refs/heads/main`; `git reset --hard`; `git restore` or `git checkout` of the whole tree (`.`, `:/`, `*`); `git clean -fd` with no path and any `git clean` that passes `-x`; `DROP DATABASE`/`DROP SCHEMA` through a database client, including one behind `docker compose exec`, `bundle exec`, `npm exec` or `poetry run`, `dropdb`, `prisma migrate reset`, `rails db:drop`, `FLUSHALL`, `supabase db reset --linked`; `shred`; `truncate` outside build, log and temp folders; `mkfs`; `dd` onto a disk, including a redirect (`dd … > /dev/sda`). `/dev/null`, `/dev/zero`, stdout and stderr are not disks. `rm -rf ~/.cache` and `rm -rf ~/old-demo` are ordinary cleanups.
5. **Skipping checks**: `--no-verify`, `git commit -n`, `git -c core.hooksPath=…`, `git config core.hooksPath` (including `git config --file <path> core.hooksPath`), `GIT_CONFIG_KEY_*` set to `core.hooksPath`, `HUSKY=0`, `SKIP=gitleaks`. Reading the setting (`git config --get core.hooksPath`) is allowed.
6. **Keys written into files**: Write, Edit, MultiEdit, `apply_patch` and MCP calls whose text gitleaks (or, without gitleaks, the kit's built-in patterns) recognises as a key. Writing a key into `.env` itself is allowed.
7. **Tampering**: any change to `.build-it-safe/` or the git hooks; shell commands that touch the agent hook settings; file edits that remove the guard from those settings or delete a name listed in `.build-it-safe/config.json`.

## Known limits

The guard is **a seatbelt, not a wall**. It stops the common ways an agent leaks a secret or breaks something, and it keeps working in bypass mode and after the agent's instructions are compacted or hijacked. It does not stop:

- **Reads that do not name the file**: `grep -r KEY .`, or a script that walks a folder and opens what it finds. Claude Code's own deny rules have the same limit.
- **A symlink to a secret that already exists.** The guard blocks creating one (`ln -s .env x`), but if `x -> .env` is already in the repository, `cat x` is allowed: the guard sees only `x`.
- **A truncating redirect** such as `> prod.db`. Blocking every `>` would stop normal work.
- **Install scripts that already ran.** `npm install` runs packages' install scripts; the guard cannot see inside them. Once a malicious package has run, rotate your keys.
- **Download first, run later, as separate tool calls**: `curl -o x.sh URL` in one call, then `sh x.sh` in a later call. Each call on its own is normal work. The same command line (`curl -o x.sh URL && sh x.sh`) is blocked.
- **Disguised commands**: code that builds a command at run time (encoded strings, unusual download tools, an interpreter that fetches a URL itself).
- **Anything outside the agent's tool calls**: what you type yourself, and programs the agent's commands start.

For a hard boundary, run the agent in a sandbox, a container or a virtual machine without your keys. `kit/SUPPORT-MATRIX.md` lists what was tested, live and with payloads.

## Supported versions

Only the latest release receives fixes.
