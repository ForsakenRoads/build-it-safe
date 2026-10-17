#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Build It Safe, Forsaken Roads® (https://github.com/ForsakenRoads/build-it-safe). See NOTICE.
"""build-it-safe guard: a pre-tool-use hook for AI coding agents.

It reads one JSON payload on stdin, the call an agent is about to make, and
exits with code 2 (block) or 0 (no objection). Exit code 2 is the documented
"block" signal in Claude Code, Codex, Cursor, GitHub Copilot and Gemini CLI,
so one script serves all of them. The reason goes to stderr, which the agent
reads.

What it stops (SECURITY.md has the exact list and the known limits):
  * reading key and secret files (.env, private keys, cloud credentials,
    /proc/<pid>/environ in any path spelling, including a backup suffix such as
    .pem.bak), by a file tool or through the shell (cat, less, head, cp,
    base64, source ..., and bash $'...' quotes);
  * environment dumps (printenv, env, set, export -p, compgen -e/-v, and
    os.environ / process.env / %ENV) and printing a secret-looking variable
    (echo $OPENAI_API_KEY);
  * destructive commands: rm -r on broad paths, find -delete or find -exec rm
    on those paths, shred, truncate outside build and temp folders,
    force-pushing or deleting main or master (including a force-push of HEAD
    while that branch is checked out), git reset --hard, git restore or
    checkout of the whole tree, git clean of the whole tree, dropping
    databases (including through docker/npm/poetry runners), mkfs, dd onto a
    disk;
  * downloaded code reaching a shell or interpreter anywhere in a pipeline
    (including a newline after the pipe, or the pipeline inside sh -c), or
    through eval, source, xargs, tee >(interpreter), a captured variable, or
    a file downloaded and executed in the same command;
  * skipping git hooks (--no-verify, core.hooksPath overrides including
    git config --file and GIT_CONFIG_KEY_*, HUSKY=0);
  * writing a literal key into a file (gitleaks stdin, or built-in patterns);
  * agents editing the kit's own files, or removing the guard from hook configs;
  * edits that delete names listed as protected in .build-it-safe/config.json.

It is a seatbelt, not a sandbox. A determined program can still read a file
without naming it. For a hard wall, run the agent in a sandbox or container.

Python 3.8+ standard library only. It never prints a secret value.
"""

import fnmatch
import glob as globmod
import json
import os
import re
import shutil
import subprocess
import sys

VERSION = "1"
BLOCK = 2
MAX_SCAN_BYTES = 2_000_000

# --------------------------------------------------------------------------
# Secret file names
# --------------------------------------------------------------------------

ALLOWED_SUFFIXES = (".example", ".sample", ".template", ".dist", ".defaults",
                    ".schema", ".pub")
ALLOWED_BASENAMES = {"example.env", "sample.env", "template.env", "known_hosts",
                     "known_hosts.old", "authorized_keys"}
KEY_EXTENSIONS = (".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".ppk",
                  ".p8", ".kdbx", ".tfstate", ".tfstate.backup")
SSH_KEY_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "id_ecdsa_sk",
                 "id_ed25519_sk", "identity"}
CREDENTIAL_NAMES = {".git-credentials", ".netrc", "_netrc", ".pypirc",
                    ".htpasswd", "serviceaccountkey.json", "credentials.json",
                    ".dev.vars", ".envrc", "auth.json", ".credentials.json",
                    ".npmrc", ".yarnrc", ".yarnrc.yml", ".pgpass", ".my.cnf"}
SECRET_GLOBS = ("client_secret*.json", "service-account*.json",
                "secrets.json", "secrets.yml", "secrets.yaml", "secrets.toml",
                ".secrets", "*.secrets")
# Paths under the home folder that hold credentials (relative to ~).
HOME_SECRET_DIRS = (".ssh", ".aws", ".gnupg", ".azure", ".kube",
                    ".config/gcloud", ".config/gh", ".docker",
                    ".claude", ".codex", ".npmrc", ".yarnrc", ".cargo/credentials",
                    ".config/op", ".password-store", ".local/share/keyrings")
HOME_SAFE_FILES = {".ssh/config", ".ssh/known_hosts", ".ssh/known_hosts.old",
                   ".ssh/authorized_keys", ".aws/config"}
# Inside ~/.claude and ~/.codex only these are secret; the rest is ordinary
# configuration an agent may read.
HOME_PARTIAL_DIRS = {".claude": {".credentials.json"}, ".codex": {"auth.json"},
                     ".docker": {"config.json"}}

# Candidate names used to test whether a shell glob such as ".e*" could reach
# a secret file.
GLOB_PROBES = (".env", ".env.local", ".env.production", ".dev.vars", "id_rsa",
               "id_ed25519", "server.key", "server.pem", "secrets.json",
               ".git-credentials", "credentials.json", "terraform.tfstate")

# Words inside interpreter code (python -c "...") that name a secret file.
SECRET_WORD_RE = re.compile(
    r"(?<![\w.-])((?:[\w./~-]*/)?(?:\.env(?:\.[\w-]+)?|[\w-]+\.env|\.dev\.vars|"
    r"id_(?:rsa|dsa|ecdsa|ed25519)|[\w-]+\.(?:pem|key|p12|pfx|tfstate)|"
    r"\.git-credentials|\.netrc|credentials\.json|serviceAccountKey\.json|"
    r"\.aws/credentials|environ))(?![\w-])")


def _home():
    return os.path.expanduser("~")


def lexical_norm(path):
    """Collapse `.`, `..` and repeated slashes without touching the filesystem.

    `/proc/./self/environ`, `//proc/self/environ` and `/proc/self/../1/environ`
    are the same files as the spellings the block list names. `os.path.normpath`
    keeps a leading `//` on POSIX, so this does not use it.
    """
    if not path:
        return path
    p = path.replace("\\", "/")
    absolute = p.startswith("/")
    parts = []
    for part in p.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts and parts[-1] != "..":
                parts.pop()
            elif not absolute:
                parts.append("..")
            continue
        parts.append(part)
    out = "/".join(parts)
    if absolute:
        out = "/" + out
    return out or ("/" if absolute else ".")


# A copy of a secret (`server.pem.bak`, `id_rsa~`) is still that secret.
_BACKUP_SUFFIXES = (".bak", ".backup", ".old", ".orig", ".save", ".copy", ".tmp", ".swp",
                    ".dpkg-old", ".dpkg-dist", ".rpmnew", ".rpmsave")


def _strip_one_backup(name):
    low = name.lower()
    for suf in _BACKUP_SUFFIXES:
        if low.endswith(suf) and len(name) > len(suf):
            return name[:-len(suf)]
    if name.endswith("~") and len(name) > 1:
        return name[:-1]
    return name


def _basename_forms(base):
    forms, seen, cur = [], set(), base
    for _ in range(4):
        if not cur or cur in seen:
            break
        seen.add(cur)
        forms.append(cur)
        nxt = _strip_one_backup(cur)
        if nxt == cur:
            break
        cur = nxt
    return forms


def _basename_secret(base):
    """Reason from one basename. The caller applies the allow-list first."""
    low = base.lower()
    if low == ".env" or low.startswith(".env.") or (low.endswith(".env") and len(low) > 4):
        return "an environment file, which holds secrets"
    if low in SSH_KEY_NAMES:
        return "a private SSH key"
    if low.endswith(KEY_EXTENSIONS):
        return "a key, certificate or state file that can hold secrets"
    if low in CREDENTIAL_NAMES:
        return "a credentials file"
    for g in SECRET_GLOBS:
        if fnmatch.fnmatch(low, g):
            return "a secrets file"
    return None


_PROC_ENVIRON_RE = re.compile(r"^/proc/[^/]+/(?:task/[^/]+/)?environ$")


def secret_reason(path, cfg=None, cwd=None):
    """Return a short reason if `path` names a secret file, else None."""
    if not path or not isinstance(path, str):
        return None
    p = path.strip().strip("'\"")
    if not p or "\n" in p or len(p) > 4096:
        return None
    p = p.replace("\\", "/")
    if "~" in p or "$" in p:
        p = os.path.expandvars(os.path.expanduser(p))
    shown = p
    p = lexical_norm(p)
    base = p.rstrip("/").rsplit("/", 1)[-1]
    cfg = cfg or {}
    joined = p if p.startswith("/") else os.path.join(cwd or os.getcwd(), p)
    absp = lexical_norm(joined)

    for pat in cfg.get("allow_paths", []):
        if any(fnmatch.fnmatch(c, pat) for c in (shown, p, base, absp)):
            return None
    for pat in cfg.get("secret_paths", []):
        if any(fnmatch.fnmatch(c, pat) for c in (shown, p, base, absp)):
            return "listed as secret in .build-it-safe/config.json"

    if _PROC_ENVIRON_RE.match(p) or _PROC_ENVIRON_RE.match(absp):
        return "a process environment, which holds secrets"
    # `.pem.example` is a sample. `.pem.bak` is not: the allow-list is the
    # original name, and only then do we look through backup suffixes.
    if base.lower() in ALLOWED_BASENAMES or base.lower().endswith(ALLOWED_SUFFIXES):
        return None
    for form in _basename_forms(base):
        reason = _basename_secret(form)
        if reason:
            return reason

    home = _home()
    if absp.startswith(home + "/"):
        rel = absp[len(home) + 1:]
        if rel in HOME_SAFE_FILES:
            return None
        for d in HOME_SECRET_DIRS:
            if rel == d or rel.startswith(d + "/"):
                only = HOME_PARTIAL_DIRS.get(d)
                if only is not None and rel[len(d) + 1:] not in only:
                    return None
                return "a credentials folder in your home directory (~/%s)" % d
    return None


def glob_reaches_secret(token, cwd, cfg):
    """True if a shell glob token could expand to a secret file."""
    if not any(c in token for c in "*?["):
        return None
    t = os.path.expanduser(token)
    base = t.rstrip("/").rsplit("/", 1)[-1]
    for probe in GLOB_PROBES:
        if fnmatch.fnmatch(probe, base) and secret_reason(probe, cfg, cwd):
            return "a pattern that can match %s" % probe
    try:
        pattern = t if os.path.isabs(t) else os.path.join(cwd, t)
        for m in globmod.glob(pattern)[:500]:
            r = secret_reason(m, cfg, cwd)
            if r:
                return "a pattern that matches %s" % os.path.relpath(m, cwd)
    except Exception:
        pass
    return None


# --------------------------------------------------------------------------
# Shell parsing (enough of POSIX sh to see words, pipes and redirects)
# --------------------------------------------------------------------------

OPS = ("&&", "||", "|&", ";;", "|", ";", "&", "(", ")", "\n")
REDIRS = ("<<<", "<<-", "<<", "<>", "<&", "<", ">>", ">|", ">&", ">", "&>>", "&>")


def extract_substitutions(cmd):
    """Pull out $(...), `...`, <(...) and >(...) bodies.

    Returns (outer, bodies, table). `outer` has each body replaced by a
    numbered placeholder that still contains `__BUILD_IT_SAFE_SUBST__`.
    `bodies` is every body, with substitutions inside them already pulled
    out. `table` maps a placeholder to that body, so a command can see only
    the substitutions that run before it."""
    table = {}
    outer, bodies = _extract_subst(cmd, [0], table)
    return outer, bodies, table


def _extract_subst(cmd, counter, table):
    out, raw_bodies, tokens, i, n = [], [], [], 0, len(cmd)
    in_s = in_d = False
    while i < n:
        c = cmd[i]
        if c == "\\" and not in_s and i + 1 < n:
            out.append(cmd[i:i + 2]); i += 2; continue
        if c == "'" and not in_d:
            in_s = not in_s; out.append(c); i += 1; continue
        if c == '"' and not in_s:
            in_d = not in_d; out.append(c); i += 1; continue
        if not in_s and (cmd.startswith("$(", i) or (not in_d and cmd.startswith(("<(", ">("), i))):
            depth, j, q = 1, i + 2, None
            while j < n and depth:
                ch = cmd[j]
                if q:
                    if ch == q:
                        q = None
                    elif ch == "\\" and q == '"':
                        j += 1
                elif ch in "'\"":
                    q = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                j += 1
            idx = counter[0]
            counter[0] += 1
            token = "__BUILD_IT_SAFE_SUBST__%d__" % idx
            raw_bodies.append(cmd[i + 2:j - 1])
            tokens.append(token)
            # $(...) stays glued to its word (s=$(curl ...) is one assignment);
            # <(...) and >(...) become a word of their own.
            prev = "".join(out[-1:])
            glue = cmd[i] == "$" or in_d or not prev or prev[-1:].isspace()
            out.append(token if glue else " " + token)
            i = j; continue
        if c == "`" and not in_s:
            j = cmd.find("`", i + 1)
            if j == -1:
                j = n
            idx = counter[0]
            counter[0] += 1
            token = "__BUILD_IT_SAFE_SUBST__%d__" % idx
            raw_bodies.append(cmd[i + 1:j])
            tokens.append(token)
            out.append(token)
            i = j + 1; continue
        out.append(c); i += 1
    outer = "".join(out)
    nested = []
    for token, raw in zip(tokens, raw_bodies):
        rewritten, inner = _extract_subst(raw, counter, table)
        table[token] = rewritten
        nested.append(rewritten)
        nested.extend(inner)
    return outer, nested


HEREDOC_RE = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][\w.-]*)\2")


def extract_heredocs(cmd):
    """Remove here-document bodies; return (command, [bodies])."""
    bodies = []
    while True:
        m = HEREDOC_RE.search(cmd)
        if not m:
            return cmd, bodies
        nl = cmd.find("\n", m.end())
        if nl == -1:
            return cmd[:m.start()] + cmd[m.end():], bodies
        delim, strip = m.group(3), bool(m.group(1))
        lines = cmd[nl + 1:].split("\n")
        body, rest_idx = [], None
        for idx, line in enumerate(lines):
            if (line.strip() if strip else line) == delim:
                rest_idx = idx + 1
                break
            body.append(line)
        bodies.append("\n".join(body))
        rest = "\n".join(lines[rest_idx:]) if rest_idx is not None else ""
        cmd = cmd[:m.start()] + " __BUILD_IT_SAFE_HEREDOC__" + cmd[m.end():nl] + "\n" + rest


def decode_ansic(text):
    """Decode the body of a bash `$'...'` quote. Unknown escapes stay literal."""
    out, i, n = [], 0, len(text)
    simple = {"\\": "\\", "'": "'", '"': '"', "a": "\a", "b": "\b", "e": "\x1b", "E": "\x1b",
              "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v", "?": "?"}
    while i < n:
        if text[i] != "\\" or i + 1 >= n:
            out.append(text[i]); i += 1; continue
        c = text[i + 1]
        if c in simple:
            out.append(simple[c]); i += 2; continue
        if c == "c" and i + 2 < n:
            out.append(chr(ord(text[i + 2].upper()) & 0x1F)); i += 3; continue
        if c == "x":
            j = i + 2
            hexd = ""
            while j < n and len(hexd) < 2 and text[j] in "0123456789abcdefABCDEF":
                hexd += text[j]; j += 1
            if hexd:
                out.append(chr(int(hexd, 16))); i = j; continue
        if c in ("u", "U"):
            width = 4 if c == "u" else 8
            hexd = text[i + 2:i + 2 + width]
            if len(hexd) == width and all(ch in "0123456789abcdefABCDEF" for ch in hexd):
                try:
                    out.append(chr(int(hexd, 16)))
                except ValueError:
                    out.append(text[i:i + 2 + width])
                i += 2 + width
                continue
        if c in "01234567":
            j, octd = i + 1, ""
            while j < n and len(octd) < 3 and text[j] in "01234567":
                octd += text[j]; j += 1
            out.append(chr(int(octd, 8))); i = j; continue
        out.append(c); i += 2
    return "".join(out)


def tokenize(cmd):
    """Split into ('w', word) and ('op', op) tokens. Quotes are removed."""
    toks, i, n = [], 0, len(cmd)
    word, have = [], False
    last_escaped = False

    def flush():
        nonlocal word, have
        if have:
            toks.append(("w", "".join(word)))
        word, have = [], False

    while i < n:
        c = cmd[i]
        if c in " \t\r":
            flush(); last_escaped = False; i += 1; continue
        if c == "\\" and i + 1 < n:
            if cmd[i + 1] == "\n":
                i += 2; continue
            word.append(cmd[i + 1]); have = True; last_escaped = True; i += 2; continue
        # Bash $'...' is an ANSI-C quote. An escaped \$ does not introduce one.
        if c == "'" and have and word and word[-1] == "$" and not last_escaped:
            word.pop()
            j, buf = i + 1, []
            while j < n and cmd[j] != "'":
                if cmd[j] == "\\" and j + 1 < n:
                    buf.append(cmd[j:j + 2]); j += 2; continue
                buf.append(cmd[j]); j += 1
            word.append(decode_ansic("".join(buf)))
            have = True
            last_escaped = False
            i = j + 1 if j < n else j
            continue
        if c == "'":
            j = cmd.find("'", i + 1)
            j = n if j == -1 else j
            word.append(cmd[i + 1:j]); have = True; last_escaped = False; i = j + 1; continue
        if c == '"':
            j, buf = i + 1, []
            while j < n and cmd[j] != '"':
                if cmd[j] == "\\" and j + 1 < n and cmd[j + 1] in '"\\$`':
                    buf.append(cmd[j + 1]); j += 2; continue
                buf.append(cmd[j]); j += 1
            word.append("".join(buf)); have = True; last_escaped = False; i = j + 1; continue
        if c == "#" and not have:
            j = cmd.find("\n", i)
            i = n if j == -1 else j
            continue
        matched = None
        if c.isdigit() and not have:
            m = re.match(r"\d+(<<<|<<|<>|<&|<|>>|>\||>&|>)", cmd[i:])
            if m:
                matched = ("r", m.group(0), m.group(1))
        if not matched:
            for r in REDIRS:
                if cmd.startswith(r, i):
                    matched = ("r", r, r)
                    break
        if not matched:
            for op in OPS:
                if cmd.startswith(op, i):
                    matched = ("op", op, op)
                    break
        if matched:
            flush()
            kind, text, core = matched
            toks.append((kind, core))
            i += len(text)
            last_escaped = False
            continue
        word.append(c); have = True; last_escaped = False; i += 1
    flush()
    return toks


def split_commands(cmd):
    """Return a list of simple commands: dicts with words, redirects, pipe flag."""
    cmds, cur = [], {"words": [], "redirs": [], "piped_from": False}
    toks = tokenize(cmd)
    i = 0
    prev_pipe = False
    while i < len(toks):
        kind, val = toks[i]
        if kind == "op":
            # A newline after `|`, `&&` or `||` is a line continuation, not a
            # new command. `curl url |\n python3` is one pipeline.
            if val == "\n" and not cur["words"] and not cur["redirs"]:
                i += 1
                continue
            if cur["words"] or cur["redirs"]:
                cmds.append(cur)
            prev_pipe = val in ("|", "|&")
            cur = {"words": [], "redirs": [], "piped_from": prev_pipe}
            i += 1
            continue
        if kind == "r":
            target = toks[i + 1][1] if i + 1 < len(toks) and toks[i + 1][0] == "w" else ""
            cur["redirs"].append((val, target))
            i += 2 if target else 1
            continue
        cur["words"].append(val)
        i += 1
    if cur["words"] or cur["redirs"]:
        cmds.append(cur)
    return cmds


WRAPPERS = {"sudo", "doas", "command", "builtin", "exec", "nohup", "time", "nice",
            "ionice", "stdbuf", "chronic", "unbuffer", "caffeinate", "env",
            "timeout", "watch", "strace", "ltrace", "xargs", "parallel", "su"}
# Options of wrapper programs that take a separate value (`sudo -u bob cmd`).
WRAPPER_VALUE_OPTS = {
    "sudo": {"-u", "-g", "-U", "-C", "-D", "-h", "-p", "-r", "-t", "-T", "-R"},
    "doas": {"-u", "-C"},
    "env": {"-u", "-C", "--unset", "--chdir", "-S", "--split-string"},
    "nice": {"-n", "--adjustment"},
    "ionice": {"-c", "-n", "-p", "-t"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "xargs": {"-I", "-L", "-n", "-P", "-s", "-d", "-E", "-a", "--arg-file", "--delimiter",
              "--max-args", "--max-procs", "--max-chars", "--replace", "--eof"},
    "parallel": {"-j", "--jobs", "-S", "--sshlogin", "-d", "--delimiter", "-a", "--arg-file", "--colsep", "-I"},
    "watch": {"-n", "--interval", "-d"},
}


def program_and_args(words):
    """Skip VAR=value assignments and wrappers; return (prog, args, assigns)."""
    assigns, i = {}, 0
    ws = list(words)
    while i < len(ws):
        w = ws[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w) and not w.startswith("="):
            k, v = w.split("=", 1)
            assigns[k] = v
            i += 1
            continue
        base = w.rsplit("/", 1)[-1]
        if base in WRAPPERS:
            i += 1
            takes = WRAPPER_VALUE_OPTS.get(base, set())
            while i < len(ws) and (ws[i].startswith("-") or (base == "env" and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", ws[i]))):
                # `env VAR=value cmd` is an assignment, same as `VAR=value cmd`.
                if base == "env" and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", ws[i]) and not ws[i].startswith("-"):
                    k, _, v = ws[i].partition("=")
                    assigns[k] = v
                    i += 1
                    continue
                if ws[i] in takes:
                    i += 1
                i += 1
            if base == "timeout" and i < len(ws) and re.match(r"^[\d.]+[smhd]?$", ws[i]):
                i += 1
            if base in ("su",) and i < len(ws) and ws[i] == "-c":
                i += 1
            continue
        return base, ws[i + 1:], assigns, ws[i]
    return "", [], assigns, ""


# --------------------------------------------------------------------------
# Rules for shell commands
# --------------------------------------------------------------------------

META_PROGS = {"ls", "stat", "test", "[", "[[", "touch", "rm", "unlink", "chmod",
              "chown", "chgrp", "mkdir", "file", "realpath", "readlink",
              "basename", "dirname", "echo", "printf", "true", ":", "du"}
GIT_META_SUBCMDS = {"check-ignore", "rm", "ls-files", "status", "mv"}
COPY_PROGS = {"cp", "install", "ln", "scp", "rsync", "mv"}
INTERPRETERS = {"python", "python2", "python3", "node", "nodejs", "deno", "bun",
                "ruby", "perl", "php", "sh", "bash", "zsh", "dash", "ksh", "fish",
                "pwsh", "powershell", "osascript", "lua", "Rscript", "awk", "gawk",
                "jq", "sed", "uv", "npx", "tsx", "ts-node"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish", "csh", "tcsh", "pwsh", "powershell"}
ENV_FILE_LOADERS = {"docker", "docker-compose", "podman", "podman-compose"}
DB_CLIENTS = {"psql", "mysql", "mariadb", "sqlite3", "mongosh", "mongo", "sqlcmd",
              "cockroach", "clickhouse-client", "clickhouse", "turso", "supabase",
              "wrangler", "prisma", "pgcli", "mycli", "redis-cli", "duckdb",
              "rails", "rake", "bin/rails", "npx", "bunx", "pnpm", "yarn"}
PROTECTED_BRANCHES_DEFAULT = ("main", "master")
KIT_DIRS = (".build-it-safe/", ".git/hooks/", ".githooks/")
READONLY_PROGS = {"cat", "less", "more", "head", "tail", "ls", "stat", "grep",
                  "rg", "wc", "diff", "file", "sha256sum", "shasum", "md5sum", "jq"}
GIT_READ_SUBCMDS = {"add", "diff", "status", "log", "show", "ls-files", "commit", "blame", "grep",
                    "check-ignore", "cat-file"}


class Block(Exception):
    def __init__(self, rule, reason, advice=""):
        super().__init__(reason)
        self.rule, self.reason, self.advice = rule, reason, advice


def git_parts(args):
    """Split `git` args into (global_opts, subcommand, sub_args)."""
    i, gopts = 0, []
    while i < len(args):
        a = args[i]
        if a in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path") and i + 1 < len(args):
            gopts.extend([a, args[i + 1]]); i += 2; continue
        if a.startswith("-"):
            gopts.append(a); i += 1; continue
        return gopts, a, args[i + 1:]
    return gopts, "", []


def current_branch(cwd, gopts):
    d = cwd
    for k, a in enumerate(gopts):
        if a == "-C" and k + 1 < len(gopts):
            d = os.path.join(cwd, gopts[k + 1])
    try:
        r = subprocess.run(["git", "-C", d, "symbolic-ref", "--short", "-q", "HEAD"],
                           capture_output=True, text=True, timeout=3)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


_GIT_CONFIG_VALUE_OPTS = {"-f", "--file", "--blob", "--default", "--comment", "--type", "-t",
                           "--get-color", "--get-colorbool"}
# Whole-tree pathspecs. A single file (`git restore src/app.py`) is ordinary.
_BROAD_GIT_PATHS = {".", "./", "..", "../", ":/", ":/*", "*", "./*", "./.", ":"}


def _git_config_positionals(sargs):
    """`git config` arguments with options such as `--file <path>` removed."""
    pos, i = [], 0
    while i < len(sargs):
        a = sargs[i]
        if a == "--":
            pos.extend(sargs[i + 1:])
            break
        if a.startswith("-"):
            opt = a.split("=", 1)[0]
            if opt in _GIT_CONFIG_VALUE_OPTS and "=" not in a:
                i += 2
                continue
            i += 1
            continue
        pos.append(a)
        i += 1
    return pos


def _hooks_path_in_git_env(assigns):
    """Git 2.31+ injects config with GIT_CONFIG_KEY_<n> / GIT_CONFIG_VALUE_<n>."""
    for k, v in assigns.items():
        ku = k.upper()
        if re.fullmatch(r"GIT_CONFIG_KEY_\d+", ku) and re.sub(r"\s+", "", v or "").lower() == "core.hookspath":
            return True
        if ku == "GIT_CONFIG_PARAMETERS" and "core.hookspath" in (v or "").lower():
            return True
    return False


def _broad_git_path(path):
    p = (path or "").strip()
    return p in _BROAD_GIT_PATHS or p.rstrip("/") in {".", "..", ":"}


def _git_pathspecs(sargs):
    """Pathspecs of checkout/restore/clean. Options that take a value are skipped."""
    if "--" in sargs:
        return [a for a in sargs[sargs.index("--") + 1:] if a != ""]
    skip_value = {"-b", "-B", "-m", "--orphan", "--conflict", "-t", "--track",
                  "--recurse-submodules", "--source", "-s"}
    paths, i = [], 0
    while i < len(sargs):
        a = sargs[i]
        if a == "--":
            return [x for x in sargs[i + 1:] if x != ""]
        if a.startswith("-"):
            opt = a.split("=", 1)[0]
            if opt in skip_value and "=" not in a:
                i += 2
                continue
            i += 1
            continue
        paths.append(a)
        i += 1
    return paths


def check_git(args, assigns, cwd, cfg):
    gopts, sub, sargs = git_parts(args)
    for k, a in enumerate(gopts):
        if a == "-c" and k + 1 < len(gopts) and gopts[k + 1].lower().startswith("core.hookspath"):
            raise Block("hook-bypass", "`git -c core.hooksPath=...` switches off the repository's safety hooks.",
                        "Run the git command without the override and fix what the hook reports.")
    if assigns.get("HUSKY") == "0" or "gitleaks" in assigns.get("SKIP", "") or "build-it-safe" in assigns.get("SKIP", ""):
        raise Block("hook-bypass", "setting HUSKY=0 or SKIP=gitleaks switches off the commit checks.",
                    "Run the command without it and fix what the check reports.")
    if _hooks_path_in_git_env(assigns):
        raise Block("hook-bypass", "setting core.hooksPath through GIT_CONFIG_KEY_* switches off the repository's safety hooks.",
                    "Run the git command without that variable and fix what the hook reports.")
    if "--no-verify" in sargs:
        raise Block("hook-bypass", "`--no-verify` skips the secret scan that runs before every commit and push.",
                    "Run it without --no-verify. If the scan reports a key, remove the key; if it is a false alarm, ask the human to allowlist it in .gitleaks.toml.")
    if sub == "config":
        keys = [a.lower() for a in _git_config_positionals(sargs)]
        reading = any(a in ("--get", "--get-all", "--list", "-l", "--get-regexp") for a in sargs)
        if keys and keys[0] == "core.hookspath" and not reading:
            raise Block("hook-bypass", "changing core.hooksPath can switch off the repository's safety hooks.",
                        "Ask the human to change git hook settings.")
    if sub == "commit":
        i = 0
        arg_opts = set("mFCcSt")
        while i < len(sargs):
            a = sargs[i]
            if a == "--":
                break
            if a.startswith("-") and not a.startswith("--") and len(a) > 1:
                for j, ch in enumerate(a[1:]):
                    if ch == "n":
                        raise Block("hook-bypass", "`git commit -n` is short for --no-verify, which skips the secret scan.",
                                    "Commit without -n and fix what the scan reports.")
                    if ch in arg_opts:
                        if j == len(a) - 2:
                            i += 1
                        break
            elif a in ("--message", "--file", "--author", "--date", "--reuse-message",
                       "--reedit-message", "--fixup", "--squash", "--template", "--trailer",
                       "--cleanup", "--pathspec-from-file"):
                i += 1
            i += 1
    protected_br = set(cfg.get("protected_branches", PROTECTED_BRANCHES_DEFAULT))
    if sub == "branch" and any(a in ("-d", "-D", "--delete") or (a.startswith("-") and not a.startswith("--") and ("d" in a or "D" in a))
                               for a in sargs):
        hit = [a for a in sargs if not a.startswith("-") and a.replace("refs/heads/", "") in protected_br]
        if hit:
            raise Block("destructive", "deleting the branch `%s` removes a protected branch." % hit[0],
                        "Ask the human; work on another branch instead.")
    if sub == "update-ref" and ("-d" in sargs or "--delete" in sargs):
        hit = [a for a in sargs if not a.startswith("-") and (a.replace("refs/heads/", "") in protected_br)]
        if hit:
            raise Block("destructive", "`git update-ref -d %s` deletes a protected branch." % hit[0],
                        "Ask the human; work on another branch instead.")
    if sub == "reset" and "--hard" in sargs:
        raise Block("destructive", "`git reset --hard` throws away uncommitted work and cannot be undone.",
                    "Use `git stash push -m <note>` to set work aside, or ask the human first.")
    if sub in ("restore", "checkout"):
        broad = [p for p in _git_pathspecs(sargs) if _broad_git_path(p)]
        if broad:
            raise Block("destructive", "`git %s` of `%s` throws away uncommitted work and cannot be undone." % (sub, broad[0]),
                        "Use `git stash push -m <note>` to set work aside, or name the one file you mean.")
    if sub == "clean":
        dry = force = ignored = False
        paths, i = [], 0
        while i < len(sargs):
            a = sargs[i]
            if a == "--":
                paths.extend(sargs[i + 1:])
                break
            if a in ("-n", "--dry-run"):
                dry = True
            elif a in ("-f", "--force"):
                force = True
            elif a in ("-x", "-X", "--ignored"):
                ignored = True
            elif a.startswith("-") and not a.startswith("--"):
                chars = a[1:]
                dry = dry or "n" in chars
                force = force or "f" in chars
                ignored = ignored or ("x" in chars or "X" in chars)
            elif not a.startswith("-"):
                paths.append(a)
            i += 1
        # `-n` is a preview. A forced clean of the whole tree, or any clean
        # that also removes ignored files, deletes work the agent did not name.
        if not dry and force and (ignored or not paths or any(_broad_git_path(p) for p in paths)):
            raise Block("destructive", "`git clean` would delete untracked work%s." % (" and ignored files" if ignored else ""),
                        "Use `git clean -n` to preview, and name a specific folder if you mean one.")
    if sub == "push":
        protected = set(cfg.get("protected_branches", PROTECTED_BRANCHES_DEFAULT))
        force = False
        positional = []
        i = 0
        while i < len(sargs):
            a = sargs[i]
            if a in ("--force", "--force-with-lease", "--force-if-includes", "--mirror") or \
                    a.startswith("--force-with-lease=") or \
                    (a.startswith("-") and not a.startswith("--") and "f" in a[1:]):
                force = True
            elif a in ("--delete", "-d"):
                force = True
                positional.append("--delete")
            elif a in ("--repo", "--receive-pack", "--exec", "-o", "--push-option"):
                i += 1
            elif not a.startswith("-"):
                positional.append(a)
            i += 1
        refspecs = [p for p in positional[1:] if p != "--delete"]
        if "--delete" in positional and len(positional) > 1:
            refspecs = [p for p in positional[2:]] if positional[0] == "--delete" else refspecs
        targets = []
        unresolved_head = False
        for r in refspecs:
            if r.startswith("+"):
                force = True
                r = r[1:]
            if r.startswith(":"):
                force = True
            dst = r.split(":", 1)[1] if ":" in r else r
            dst = dst.replace("refs/heads/", "")
            # `git push origin HEAD` updates the branch that is checked out.
            # The destination text is the word HEAD, which is not itself a
            # protected branch name.
            if dst in ("HEAD", "@"):
                branch = current_branch(cwd, gopts)
                if branch:
                    dst = branch
                else:
                    unresolved_head = True
            targets.append(dst)
        if not refspecs:
            if "--all" in sargs or "--mirror" in sargs:
                targets = list(protected)
            else:
                targets = [current_branch(cwd, gopts)]
        hit = [t for t in targets if t in protected]
        if force and unresolved_head:
            raise Block("destructive", "force-pushing `HEAD` rewrites the checked-out branch, and that branch could not be read.",
                        "Push to a new branch and open a pull request, or ask the human.")
        if force and hit:
            raise Block("destructive", "force-pushing or deleting `%s` rewrites the shared history of a protected branch." % hit[0],
                        "Push to a new branch and open a pull request, or ask the human.")


# Direct children of ~ that are a person's files or a credential store.
# `~/.cache` and one old checkout (`~/old-demo`) are ordinary cleanups.
# `~/Documents` and `~/.ssh` are not.
_HOME_BROAD_CHILDREN = {
    "documents", "desktop", "downloads", "pictures", "photos", "movies", "videos",
    "music", "library", "applications", "public", "templates", "onedrive", "dropbox",
    ".ssh", ".aws", ".gnupg", ".azure", ".kube", ".docker", ".claude", ".codex",
    ".config", ".password-store", ".local", ".cargo", ".mozilla", ".pki", ".cert",
    ".certs", ".npm", ".yarn", ".thunderbird", ".kde", ".gnome2", ".gnupg",
}


def _home_child_broad(name):
    return (name or "").lower() in _HOME_BROAD_CHILDREN


def broad_rm_target(t, cwd, project):
    home = _home()
    raw = t
    t = t.replace("${HOME}", home).replace("$HOME", home)
    t = os.path.expanduser(t)
    if raw in ("*", ".*", "./*", "./.*", "/*", "~/*", "~/.*"):
        if raw.startswith(("/", "~")) or os.path.realpath(cwd) in (project, home, "/"):
            return raw
    stripped = t.rstrip("/*") if t not in ("/", "/*") else "/"
    absp = os.path.normpath(stripped if os.path.isabs(stripped) else os.path.join(cwd, stripped or "."))
    if absp == "/" or absp.count("/") <= 1:
        return raw
    if absp == home or (os.path.dirname(absp) == home and _home_child_broad(os.path.basename(absp))):
        return raw
    if project and (absp == project or project.startswith(absp + "/")):
        return raw
    if os.path.basename(absp) == ".git":
        return raw
    return None


def check_rm(args, cwd, project):
    recursive = False
    targets, end_opts = [], False
    for a in args:
        if not end_opts and a == "--":
            end_opts = True
            continue
        if not end_opts and a.startswith("-") and len(a) > 1:
            if a == "--no-preserve-root":
                raise Block("destructive", "`rm --no-preserve-root` can erase the whole disk.")
            if a in ("--recursive",) or (not a.startswith("--") and ("r" in a or "R" in a)):
                recursive = True
            continue
        targets.append(a)
    if not recursive:
        return
    for t in targets:
        b = broad_rm_target(t, cwd, project)
        if b:
            raise Block("destructive", "`rm -r %s` would delete a whole folder tree (%s) that is too broad to remove safely." % (t, b),
                        "Delete the specific build folder instead (for example `rm -rf dist`), or ask the human.")


# --------------------------------------------------------------------------
# Fetch and run: downloaded code reaching a shell or interpreter
# --------------------------------------------------------------------------

FETCHERS = {"curl", "wget", "wget2", "fetch", "aria2c", "http", "https", "xh", "xhs", "curlie",
            "httpie", "lwp-request", "get", "iwr", "irm", "invoke-webrequest", "invoke-restmethod"}
CODE_FLAGS = {"-c", "-e", "-E", "-m", "-r", "--eval", "-p", "--print", "-n", "-command", "-encodedcommand",
              "-file", "--command"}
STDIN_NAMES = {"-", "/dev/stdin", "/proc/self/fd/0", "/dev/fd/0"}
EXEC_INTERPRETERS = {"python", "python2", "python3", "perl", "ruby", "node", "nodejs", "php", "lua",
                     "pwsh", "powershell", "osascript", "rscript", "tclsh", "bun", "deno"}
PLACEHOLDER = "__BUILD_IT_SAFE_SUBST__"
VAR_REF_RE = re.compile(r"\$(?:\{(?!#)([A-Za-z_][A-Za-z0-9_]*)[^}]*\}|([A-Za-z_][A-Za-z0-9_]*)|env:([A-Za-z_][A-Za-z0-9_]*))", re.I)
# Every shell and interpreter, longest name first so `python3` wins over `python`.
_PSUB_NAMES = sorted(SHELLS | EXEC_INTERPRETERS, key=len, reverse=True)
TEE_TO_SHELL_RE = re.compile(
    r">\(\s*(?:sudo\s+(?:-\S+\s+)*)?(?:" + "|".join(re.escape(n) for n in _PSUB_NAMES) + r")(?:[0-9.]*)\b",
    re.I)


def head_prog(words):
    """Like program_and_args, but xargs and parallel count as programs."""
    i, ws = 0, list(words)
    while i < len(ws):
        w = ws[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            i += 1
            continue
        base = w.rsplit("/", 1)[-1].lower()
        if base in WRAPPERS and base not in ("xargs", "parallel"):
            i += 1
            takes = WRAPPER_VALUE_OPTS.get(base, set())
            while i < len(ws) and (ws[i].startswith("-") or (base == "env" and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", ws[i]))):
                if ws[i] in takes:
                    i += 1
                i += 1
            if base == "timeout" and i < len(ws) and re.match(r"^[\d.]+[smhd]?$", ws[i]):
                i += 1
            continue
        return base, ws[i + 1:]
    return "", []


def var_refs(text):
    return [a or b or c for a, b, c in VAR_REF_RE.findall(text or "")]


def shell_reads_stdin(args):
    """Does `sh ARGS` take its program from standard input?"""
    i = 0
    while i < len(args):
        a = args[i]
        if a in STDIN_NAMES:
            return True
        if a == "--":
            return i + 1 >= len(args) or args[i + 1] in STDIN_NAMES
        if a.startswith("-") and len(a) > 1:
            if a in ("-c",) or (not a.startswith("--") and "c" in a[1:]):
                return False                      # sh -c 'code': stdin is data
            if a in ("-o", "+o", "-O", "+O", "--rcfile", "--init-file"):
                i += 1
            i += 1
            continue
        return False                              # sh script.sh: stdin is data
    return True


def interpreter_reads_stdin(args):
    for k, a in enumerate(args):
        if a in STDIN_NAMES:
            return True
        if a.lower() in CODE_FLAGS or (a.startswith("-") and not a.startswith("--") and len(a) > 1
                                       and a[1:2] in "cemrE" and a.lower() not in ("-u",)):
            return False
        if not a.startswith("-"):
            return False                          # a script file: stdin is data
    return True


def runs_stdin(words):
    """Is this pipeline stage a shell or interpreter executing what it reads?"""
    name, args = head_prog(words)
    if name in ("xargs", "parallel"):
        rest = [a for a in args if not a.startswith("-")]
        if name == "parallel" and not rest:
            return True                           # parallel runs each input line as a command
        return any(a.rsplit("/", 1)[-1].lower() in SHELLS | EXEC_INTERPRETERS for a in args) or "-c" in args
    if name in SHELLS:
        return shell_reads_stdin(args)
    if name in EXEC_INTERPRETERS:
        return interpreter_reads_stdin(args)
    if name in ("iex", "invoke-expression"):
        return True
    if name in ("source", "."):
        return any(a in STDIN_NAMES for a in args)
    if name == "eval":
        return any(PLACEHOLDER in a for a in args)
    return False


def runs_code_arg(words, is_fetched):
    """Does this command execute, as code, an argument that holds fetched text?
    is_fetched(arg) says whether an argument carries downloaded content."""
    name, args = head_prog(words)
    if name in ("eval", "source", ".", "iex", "invoke-expression"):
        return any(is_fetched(a) for a in args)
    if name in SHELLS or name in EXEC_INTERPRETERS:
        for k, a in enumerate(args):
            if a.lower() in CODE_FLAGS or (name in SHELLS and a.startswith("-") and not a.startswith("--") and "c" in a[1:]):
                return k + 1 < len(args) and is_fetched(args[k + 1])
            if a.startswith("-"):
                continue
            return is_fetched(a)                  # bash <(curl ...): the script itself was fetched
    return False


def check_fetch_and_run(pieces, bodies, here_strings):
    """Block a download whose content reaches a shell or interpreter."""
    def has_fetch(text):
        for c in split_commands(text):
            if head_prog(c["words"])[0] in FETCHERS:
                return True
        return False

    fetch_subst = any(has_fetch(b) for b in bodies)
    tainted = set()

    def is_fetched(arg):
        return (fetch_subst and PLACEHOLDER in arg) or any(v in tainted for v in var_refs(arg))

    reason = ("downloaded code would run without anyone reading it.",
              "Download the script to a file, show it to the human, and run it only after they approve; or use the project's package manager.")
    for piece in pieces:
        cmds = split_commands(piece)
        # Variables that capture a download: s=$(curl ...), export s=`wget -O- ...`
        for c in cmds:
            name, args = head_prog(c["words"])
            cand = [w for w in c["words"] if "=" in w and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w)]
            if name in ("export", "local", "declare", "typeset", "readonly"):
                cand += [a for a in args if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", a)]
            for w in cand:
                k, v = w.split("=", 1)
                if is_fetched(v):
                    tainted.add(k)
        source_seen = False
        for c in cmds:
            if not c.get("piped_from"):
                source_seen = False
            name = head_prog(c["words"])[0]
            fetched_here = name in FETCHERS or any(is_fetched(w) for w in c["words"]) or \
                any(is_fetched(t) for op, t in c["redirs"] if op == "<<<")
            if source_seen and runs_stdin(c["words"]):
                raise Block("pipe-to-shell", "this pipeline sends a download into `%s`, so %s" % (name, reason[0]), reason[1])
            if runs_code_arg(c["words"], is_fetched) or (
                    any(is_fetched(t) for op, t in c["redirs"] if op == "<<<") and (name in SHELLS or name in EXEC_INTERPRETERS)):
                raise Block("pipe-to-shell", "`%s` would execute downloaded text, so %s" % (name, reason[0]), reason[1])
            if fetched_here:
                source_seen = True


CURL_PIPE_RE = re.compile(
    r"\b(curl|wget|fetch|aria2c|http|https|iwr|irm|invoke-webrequest|invoke-restmethod)\b[^|;&\n]*"
    r"\|\s*(?:sudo\s+(?:-\S+\s+)*)?(?:env\s+(?:\S+=\S*\s+)*)?"
    r"(?:(?:ba|z|da|k|fi|c|tc)?sh|iex|invoke-expression)\b(?!\s+[\w./-]+\.(?:sh|bash)\b)",
    re.I)
SHELL_SUBST_RE = re.compile(r"\b(?:(?:ba|z|da|k)?sh|source|\.)\s+(?:-\w+\s+)*<\(\s*(?:curl|wget)\b", re.I)
SHELL_C_RE = re.compile(r"\b(?:(?:ba|z|da|k)?sh)\s+-c\s+[\"']?\s*(?:\$\(|`)\s*(?:curl|wget)\b", re.I)
DB_DROP_RE = re.compile(r"\bdrop\s+(?:database|schema)\b|\bdropDatabase\s*\(|\bflushall\b|\bflushdb\b", re.I)
DB_TOOL_RE = re.compile(r"\bprisma\s+migrate\s+reset\b|\b(?:rails|rake)\s+db:(?:drop|reset|purge)\b|"
                        r"\bsupabase\s+db\s+reset\b[^\n;&|]*--(?:linked|db-url)", re.I)


def is_kit_path(tok, cwd, project, configs=True):
    """The kit's own files and git hooks; with configs=True also the agent
    configs that run the guard (shell commands may not touch those at all;
    file-tool edits to them are checked by check_protected instead)."""
    p = tok.replace("\\", "/")
    if not p or p.startswith("-"):
        return False
    absp = os.path.normpath(p if os.path.isabs(p) else os.path.join(cwd, p))
    root = project or cwd
    for d in KIT_DIRS:
        dd = os.path.join(root, d.rstrip("/"))
        if absp == dd or absp.startswith(dd + "/"):
            return True
    if not configs:
        return False
    rel = os.path.relpath(absp, root).replace("\\", "/")
    return rel in HOOK_CONFIG_FILES or rel.startswith(".github/hooks/")


def token_secret(tok, cwd, cfg):
    if tok.startswith("-") and "=" in tok:
        tok = tok.split("=", 1)[1]
    elif tok.startswith("-"):
        return None
    if tok.startswith("@"):
        tok = tok[1:]
    return secret_reason(tok, cfg, cwd) or glob_reaches_secret(tok, cwd, cfg)


_SAFE_DEVICES = {"null", "zero", "stdin", "stdout", "stderr", "tty", "full",
                 "random", "urandom", "console", "ptmx", "fd"}
_FIND_NAME_OPTS = {"-name", "-iname", "-path", "-ipath", "-wholename", "-iwholename", "-regex", "-iregex"}
_FIND_MATCH_ALL = {"*", ".*", "./*", "/*", "**", "**/*", "./**"}
_CODE_STRING_RE = re.compile(r"""(['"])((?:\\.|(?!\1).)*)\1""", re.S)
_SEARCH_VALUE_OPTS = {
    "-e", "--regexp", "-f", "--file", "-m", "--max-count", "-A", "--after-context",
    "-B", "--before-context", "-C", "--context", "--include", "--exclude",
    "--exclude-dir", "--include-dir", "-g", "--glob", "--iglob", "-t", "--type",
    "-T", "--type-not", "--color", "--label", "--binary-files", "-d", "--directories",
}


def is_disk_device(path):
    """True for `/dev/sda` and the like. Not for `/dev/null`, `/dev/zero`, stdout or stderr."""
    if not path or not isinstance(path, str) or path.startswith("-"):
        return False
    p = lexical_norm(os.path.expanduser(path))
    if not p.startswith("/dev/"):
        return False
    rest = p[len("/dev/"):]
    if not rest:
        return False
    first = rest.split("/", 1)[0]
    if first in _SAFE_DEVICES or rest in _SAFE_DEVICES:
        return False
    if first.startswith("tty") and (len(first) == 3 or first[3:].isdigit()):
        return False
    return True


def _abs_here(path, cwd):
    home = _home()
    raw = os.path.expanduser((path or "").replace("${HOME}", home).replace("$HOME", home))
    if not os.path.isabs(raw):
        raw = os.path.join(cwd, raw or ".")
    return os.path.normpath(raw)


def _catastrophic_root(root, cwd):
    """`/`, the home directory, or a shallow absolute path such as `/usr`."""
    absp = _abs_here(root, cwd)
    return absp in ("/", _home()) or absp.count("/") <= 1


def _find_roots(args):
    roots = []
    for a in args:
        if a.startswith("-") or a in ("(", ")", "!", ",", ";"):
            break
        roots.append(a)
    return roots or ["."]


def _find_narrowed(args):
    """True when -name/-path/-regex limits the walk to something other than everything."""
    for i, a in enumerate(args[:-1]):
        if a in _FIND_NAME_OPTS and args[i + 1] not in _FIND_MATCH_ALL and set(args[i + 1]) != {"*"}:
            return True
    return False


def _find_exec_deletes(args):
    i = 0
    while i < len(args):
        if args[i] in ("-exec", "-execdir", "-ok", "-okdir"):
            j, cmd = i + 1, []
            while j < len(args) and args[j] not in (";", "+"):
                cmd.append(args[j])
                j += 1
            prog = cmd[0].rsplit("/", 1)[-1] if cmd else ""
            if prog in ("rm", "unlink", "rmdir", "shred", "wipe"):
                return True
            if prog in SHELLS and re.search(r"\brm\b", " ".join(cmd)):
                return True
            i = j + 1
            continue
        i += 1
    return False


def _search_pattern_indexes(args):
    """Indexes of grep/rg arguments that are the search text, not files to read."""
    idxs, positionals, seen_flag, i = set(), [], False, 0
    while i < len(args):
        a = args[i]
        if a == "--":
            rest = list(range(i + 1, len(args)))
            if not seen_flag and rest:
                idxs.add(rest[0])
            return idxs
        if a.startswith("-") and a != "-":
            opt = a.split("=", 1)[0]
            if opt in ("-e", "--regexp") or (not a.startswith("--") and "e" in a[1:] and a[1:].endswith("e")):
                seen_flag = True
                if "=" not in a and i + 1 < len(args):
                    idxs.add(i + 1)
                    i += 2
                    continue
            elif opt in _SEARCH_VALUE_OPTS and "=" not in a:
                i += 2
                continue
            i += 1
            continue
        positionals.append(i)
        i += 1
    if not seen_flag and positionals:
        idxs.add(positionals[0])
    return idxs


def _code_literals(blob):
    found = []
    for m in _CODE_STRING_RE.finditer(blob or ""):
        body = re.sub(r"\\([\\'\"])", r"\1", m.group(2))
        found.append(body)
    return found


def _py_env_problem(blob):
    if re.search(r"\bos\s*\.\s*environ\b(?!\s*(?:\.get\s*\(|\[\s*['\"]))", blob):
        return "the whole environment"
    for m in re.finditer(r"""\bos\s*\.\s*(?:environ\s*(?:\.get\s*\(|\[)|getenv\s*\()\s*(['"])([A-Za-z_][A-Za-z0-9_]*)\1""", blob):
        if secret_var(m.group(2)):
            return "$" + m.group(2)
    return None


def _node_env_problem(blob):
    if re.search(r"""process\s*(?:\.\s*env\b|\[\s*['\"]env['\"]\s*\])(?!\s*(?:\[\s*['\"]|\.\s*[A-Za-z_]))""", blob):
        return "the whole environment"
    for m in re.finditer(
            r"""process\s*(?:\.\s*env|\[\s*['\"]env['\"]\s*\])\s*(?:\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]|\.([A-Za-z_][A-Za-z0-9_]*))""",
            blob):
        key = m.group(1) or m.group(2)
        if secret_var(key):
            return "$" + key
    return None


def _perl_env_problem(blob):
    if re.search(r"(?:keys|values|each)\s*\(?\s*%\s*ENV\b", blob) or re.search(r"(?<![\w$])%\s*ENV\b", blob):
        return "the whole environment"
    for m in re.finditer(r"""\$ENV\s*\{\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?\s*\}""", blob):
        if secret_var(m.group(1)):
            return "$" + m.group(1)
    return None


def code_env_problem(prog, blob):
    """A reason if this interpreter snippet prints environment values."""
    p = (prog or "").lower()
    if p in ("python", "python2", "python3", "uv"):
        return _py_env_problem(blob)
    if p in ("node", "nodejs", "bun", "deno", "tsx", "ts-node"):
        return _node_env_problem(blob)
    if p == "perl":
        return _perl_env_problem(blob)
    return None


def check_simple(cmd, cwd, project, cfg, context):
    words, redirs = cmd["words"], cmd["redirs"]
    prog, args, assigns, raw_prog = program_and_args(words)

    for op, target in redirs:
        if op.startswith("<") and op not in ("<<", "<<-", "<<<") and target:
            r = token_secret(target, cwd, cfg)
            if r:
                raise Block("secret-read", "`%s` is %s, and redirecting it into a command reads it." % (target, r),
                            "Read `.env.example` for variable names, and ask the human about values.")
        if op.startswith(">") or op in ("&>", "&>>", ">&"):
            if target and is_disk_device(target):
                raise Block("destructive", "redirecting output onto `%s` can overwrite a whole disk." % target,
                            "Write to a file under the project or /tmp, not to a disk device.")
            if target and is_kit_path(target, cwd, project):
                raise Block("kit-tamper", "agents may not overwrite the Build It Safe Kit's own files (%s)." % target,
                            "Ask the human to change the kit.")

    check_env_dump(words, redirs, cwd)
    if not prog:
        return
    if prog == "git":
        check_git(args, assigns, cwd, cfg)
    if prog == "shred" or prog == "wipe":
        raise Block("destructive", "`%s` overwrites files so they can never be recovered." % prog,
                    "Delete build output with `rm` instead, or ask the human.")
    if prog == "truncate":
        check_truncate(args, cwd)
    if prog in ("rm", "rmdir", "unlink") or raw_prog.endswith("/rm"):
        check_rm(args, cwd, project)
    if prog.startswith("mkfs"):
        raise Block("destructive", "`%s` can overwrite a whole disk." % prog)
    if prog == "dd":
        devs = [a.split("=", 1)[1] for a in args if a.startswith("of=")]
        bad = [d for d in devs if is_disk_device(d)]
        if bad:
            raise Block("destructive", "`dd` can overwrite a whole disk (%s)." % bad[0])
    if prog in ("dropdb", "dropuser"):
        raise Block("destructive", "`%s` deletes a database or its owner. A dropped database is gone unless a backup restores it." % prog,
                    "Ask the human. Never run this against production.")
    if prog == "find" and ("-delete" in args or _find_exec_deletes(args)):
        roots = _find_roots(args)
        root = roots[0]
        if broad_rm_target(root, cwd, project):
            # `find . -name '*.pyc' -delete` is a cleanup. `find ~ -name x -delete`
            # and `find . -delete` are not: home, `/` and shallow paths stay blocked
            # even with a name predicate, and so does an unfiltered walk.
            if _catastrophic_root(root, cwd) or not _find_narrowed(args):
                how = "-delete" if "-delete" in args else "-exec"
                raise Block("destructive", "`find %s %s` would delete across a whole folder tree." % (root, how))

    # Secret files named on the command line.
    hits = []
    for idx, w in enumerate(args):
        if PLACEHOLDER in w:
            continue
        r = token_secret(w, cwd, cfg)
        if r:
            hits.append((idx, w, r))
    if prog in ("grep", "egrep", "fgrep", "rg", "ag", "ack"):
        # `grep -n .env README.md` searches for the text. `grep KEY .env` reads the file.
        skip = _search_pattern_indexes(args)
        hits = [h for h in hits if h[0] not in skip]
    # Interpreter code (python -c, node -e, awk programs, heredocs).
    # A string is a file only when the whole literal is a path. A sentence that
    # mentions `.env` is not an open() of that file. `process.env` is handled
    # as an environment dump, not as a file whose name ends in `.env`.
    code_hits = []
    if prog in INTERPRETERS or prog in DB_CLIENTS:
        blobs = [w for w in args if " " in w or "(" in w or "'" in w or '"' in w or ".env" in w or "environ" in w or "ENV" in w]
        blobs += context.get("heredocs", []) if prog in INTERPRETERS else []
        for blob in blobs:
            if prog in INTERPRETERS:
                why = code_env_problem(prog, blob)
                if why:
                    raise Block("env-dump", "this %s code prints %s, which can include keys." % (prog, why), DUMP_ADVICE)
            for lit in _code_literals(blob):
                if not lit or any(ch.isspace() for ch in lit):
                    continue
                r = secret_reason(lit, cfg, cwd)
                if r:
                    code_hits.append((lit, r))
    if any(PLACEHOLDER in a for a in args) and context.get("subst_secret") and prog not in META_PROGS:
        name, r = context["subst_secret"][0]
        raise Block("secret-read", "`%s` is %s, and this command reads it through `$(...)`." % (name, r),
                    "Read `.env.example` for variable names; the app loads the real file itself.")
    if not hits and not code_hits:
        return
    if code_hits and prog in INTERPRETERS:
        name, r = code_hits[0]
        raise Block("secret-read", "this %s code opens `%s`, which is %s." % (prog, name, r),
                    "Read `.env.example` for variable names, and ask the human about values.")
    if not hits:
        return
    idx, name, r = hits[0]
    if prog in META_PROGS and not context.get("feeds_xargs"):
        return
    if prog == "git":
        _, sub, _ = git_parts(args)
        if sub in GIT_META_SUBCMDS:
            return
        if sub == "add":
            raise Block("secret-commit", "`%s` is %s; adding it to git would publish it with the next push." % (name, r),
                        "Add it to .gitignore instead (`echo '%s' >> .gitignore`)." % os.path.basename(name))
    if prog in COPY_PROGS:
        positional = [w for w in args if not w.startswith("-")]
        if positional and all(i == len(args) - 1 or args[i] == positional[-1] for i, _, _ in hits):
            return  # the secret file is only the destination: cp .env.example .env, mv .env.example .env
    if prog in ENV_FILE_LOADERS:
        if all(args[i - 1] == "--env-file" or args[i].startswith("--env-file=") for i, _, _ in hits if i > 0) and \
                all(i > 0 for i, _, _ in hits):
            return
    if prog in ("node", "nodejs", "bun", "deno") and all(args[i].startswith("--env-file") for i, _, _ in hits) and \
            not any(a in ("-e", "--eval", "-p", "--print") for a in args):
        return
    if prog == "find" and not any(a in ("-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fls") for a in args):
        return
    raise Block("secret-read", "`%s` is %s. Agents must not read, copy or print it (`%s ...`)." % (name, r, prog),
                "Read `.env.example` for variable names; the app loads the real file itself. Ask the human if you need a value checked.")


# --------------------------------------------------------------------------
# Environment dumps and secret variables
# --------------------------------------------------------------------------

PRINTERS = {"echo", "printf", "print", "write-output", "write-host", "printenv"}
DUMP_ADVICE = ("Name the variable you need (for example `printenv PATH`). If a task needs a secret's value, "
               "ask the human; the app reads it from the environment itself.")


# `PRIVATE_IP` is an address. `PUBLIC_KEY` and `CACHE_KEY` are not credentials.
# `MAX_TOKENS` is a count: TOKEN as its own word still is a credential.
_PRIVATE_NET = {"IP", "IPS", "ADDR", "ADDRESS", "HOST", "HOSTNAME", "PORT", "DNS",
                "NETWORK", "SUBNET", "CIDR", "MASK", "GATEWAY", "INTERFACE"}


def secret_var(name):
    n = (name or "").upper()
    if not n:
        return False
    if re.search(r"(^|_)PUBLIC_KEYS?$", n) and not re.search(r"SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL", n):
        return False
    if re.search(r"(^|_)CACHE_KEYS?$", n) and not re.search(r"SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL", n):
        return False
    parts = re.findall(r"[A-Z0-9]+", n)
    if any(w in n for w in ("SECRET", "PASSWORD", "PASSWD", "CREDENTIAL", "DATABASE_URL")):
        return True
    if "TOKEN" in parts:
        return True
    if "PASS" in parts or n.endswith("PASS"):
        return True
    if "PRIVATE" in parts and any(p in _PRIVATE_NET for p in parts):
        return False
    if "PRIVATE" in parts:
        return True
    return bool(any(p in ("KEY", "KEYS") for p in parts) or n.endswith("KEY") or n.endswith("KEYS"))


def check_env_dump(words, redirs, cwd):
    name, args = head_prog(words)
    raw = [w for w in words if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w)]
    # `env` with no command prints every variable: env, env | grep KEY, env -0, env -u X
    i = 0
    while i < len(raw) and raw[i].rsplit("/", 1)[-1].lower() in ("sudo", "doas", "command", "builtin", "exec", "nohup", "time"):
        i += 1
    if i < len(raw) and raw[i].rsplit("/", 1)[-1] == "env":
        rest = raw[i + 1:]
        j, runs_command = 0, False
        while j < len(rest):
            a = rest[j]
            if a in ("-S", "--split-string") or a.startswith("--split-string="):
                runs_command = True               # env -S "cmd ...": runs a command
                break
            if a in ("-u", "-C", "--unset", "--chdir"):
                j += 2
                continue
            if a.startswith("-") or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", a):
                j += 1
                continue
            runs_command = True
            break
        if not runs_command:
            raise Block("env-dump", "`env` with no command prints every environment variable, including any keys.", DUMP_ADVICE)
    if name == "printenv":
        names = [a for a in args if not a.startswith("-")]
        if not names:
            raise Block("env-dump", "`printenv` with no name prints every environment variable, including any keys.", DUMP_ADVICE)
        bad = [n for n in names if secret_var(n)]
        if bad:
            raise Block("env-dump", "`printenv %s` would print a secret." % bad[0], DUMP_ADVICE)
    if name == "set" and not args:
        raise Block("env-dump", "`set` with no arguments prints every shell variable, including any keys.", DUMP_ADVICE)
    if name == "export":
        printing = (not args) or any(
            a == "-p" or (a.startswith("-") and not a.startswith("--") and "p" in a[1:]) for a in args)
        names = [a for a in args if not a.startswith(("-", "+")) and not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", a)]
        if printing and not names:
            raise Block("env-dump", "`export -p` prints every exported variable, including any keys.", DUMP_ADVICE)
        if printing and any(secret_var(n) for n in names):
            raise Block("env-dump", "`export -p %s` would print a secret variable." % names[0], DUMP_ADVICE)
    if name in ("declare", "typeset"):
        flags = "".join(a[1:] for a in args if a.startswith("-"))
        names = [a for a in args if not a.startswith(("-", "+"))]
        if not names and (not flags or "p" in flags or "x" in flags):
            raise Block("env-dump", "`%s %s` prints every variable, including any keys." % (name, " ".join(args)), DUMP_ADVICE)
        if "p" in flags and any(secret_var(n.split("=", 1)[0]) for n in names if "=" not in n):
            raise Block("env-dump", "`%s -p` would print a secret variable." % name, DUMP_ADVICE)
    if name == "compgen":
        shorts = "".join(a[1:] for a in args if a.startswith("-") and not a.startswith("--"))
        actions = [args[i + 1] for i, a in enumerate(args) if a == "-A" and i + 1 < len(args)]
        if "e" in shorts or "v" in shorts or "export" in actions or "variable" in actions:
            raise Block("env-dump", "`compgen %s` lists shell variables, including the names of any keys." % " ".join(args),
                        DUMP_ADVICE)
    if name in ("get-childitem", "gci", "dir", "ls", "get-item", "gi") and any(re.match(r"(?i)^env:\\?\*?$", a) for a in args):
        raise Block("env-dump", "listing `env:` prints every environment variable, including any keys.", DUMP_ADVICE)
    # Printing a secret-looking variable: echo $OPENAI_API_KEY, printf '%s' "$DB_PASSWORD"
    if name in PRINTERS or (name in ("cat", "tee", "base64", "xxd", "od") and any(op == "<<<" for op, _ in redirs)):
        texts = list(args) + [t for op, t in redirs if op == "<<<"]
        bad = [v for t in texts for v in var_refs(t) if secret_var(v)]
        if bad:
            outs = [t for op, t in redirs if op.startswith(">") or op in ("&>", "&>>")]
            if outs and all("environment" in (secret_reason(t, None, cwd) or "") for t in outs):
                return                            # echo "KEY=$KEY" >> .env: the value goes to the env file, not the screen
            raise Block("env-dump", "this would print `$%s`, which looks like a secret." % bad[0], DUMP_ADVICE)


BUILD_OR_TEMP_DIRS = {"dist", "build", "out", ".next", ".nuxt", ".output", ".svelte-kit", "target", "coverage",
                      "node_modules", "tmp", "temp", ".tmp", ".cache", "cache", "__pycache__", ".turbo",
                      ".parcel-cache", "_regen", "log", "logs", ".pytest_cache", ".mypy_cache"}


def is_build_or_temp(path, cwd):
    p = os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))
    tmp_roots = {"/tmp", "/var/tmp", "/private/tmp", os.environ.get("TMPDIR", "/tmp").rstrip("/") or "/tmp"}
    if any(p == t or p.startswith(t + "/") for t in tmp_roots):
        return True
    rel = os.path.relpath(p, cwd)
    parts = rel.replace("\\", "/").split("/")[:-1]
    return any(x in BUILD_OR_TEMP_DIRS for x in parts) or p.endswith(".log")


def check_truncate(args, cwd):
    files, i = [], 0
    while i < len(args):
        a = args[i]
        if a in ("-s", "--size", "-r", "--reference"):
            i += 2
            continue
        if not a.startswith("-") or a == "-":
            files.append(a)
        i += 1
    bad = [f for f in files if not is_build_or_temp(f, cwd)]
    if bad:
        raise Block("destructive", "`truncate` would wipe the contents of `%s`, which is not build output or a temp file." % bad[0],
                    "Ask the human before emptying project files.")


_PKG_RUN = {
    "bundle": {"exec"}, "poetry": {"run"}, "pipenv": {"run"}, "uv": {"run"},
    "npm": {"exec", "x"}, "yarn": {"exec", "dlx"}, "pnpm": {"exec", "dlx"},
    "bun": {"x"}, "composer": {"exec"},
}
_DOCKER_VALUE = {"-u", "--user", "-w", "--workdir", "-e", "--env", "--env-file", "--index",
                 "--entrypoint", "-v", "--volume", "--name", "--network", "--hostname",
                 "-l", "--label", "--mount", "-p", "--publish"}
_DOCKER_GLOBAL = {"-c", "--context", "--host", "-H", "--config", "--log-level"}
_COMPOSE_VALUE = {"-f", "--file", "--project-name", "-p", "--profile", "--env-file", "--project-directory"}
_FETCH_WORDS = ("curl", "wget", "fetch", "aria2c", "iwr", "invoke-webrequest")


def _skip_opts(words, i, value_opts):
    n = len(words)
    while i < n:
        a = words[i]
        if a == "--":
            return i + 1
        if not a.startswith("-"):
            return i
        opt = a.split("=", 1)[0]
        if opt in value_opts and "=" not in a:
            i += 2
            continue
        i += 1
    return i


def _wrapper_next(words, i, base):
    takes = WRAPPER_VALUE_OPTS.get(base, set())
    n = len(words)
    while i < n and (words[i].startswith("-") or (base == "env" and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[i]))):
        if base == "env" and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[i]) and not words[i].startswith("-"):
            i += 1
            continue
        if words[i] in takes:
            i += 1
        i += 1
    if base == "timeout" and i < n and re.match(r"^[\d.]+[smhd]?$", words[i]):
        i += 1
    if base == "su" and i < n and words[i] == "-c":
        i += 1
    return i


def _runner_inner(words, i, base):
    """Index of the command after docker/npm/poetry/bundle, or None."""
    n, low = len(words), base.lower()
    if low in ("docker", "podman"):
        j = _skip_opts(words, i + 1, _DOCKER_GLOBAL)
        if j >= n:
            return None
        if words[j] == "compose":
            j = _skip_opts(words, j + 1, _COMPOSE_VALUE)
            if j < n and words[j] in ("exec", "run"):
                j = _skip_opts(words, j + 1, _DOCKER_VALUE)
                if j < n and not words[j].startswith("-"):
                    j += 1
                return j
            return None
        if words[j] in ("exec", "run"):
            j = _skip_opts(words, j + 1, _DOCKER_VALUE)
            if j < n and not words[j].startswith("-"):
                j += 1
            return j
        return None
    if low in ("docker-compose", "podman-compose"):
        j = _skip_opts(words, i + 1, _COMPOSE_VALUE)
        if j < n and words[j] in ("exec", "run"):
            j = _skip_opts(words, j + 1, _DOCKER_VALUE)
            if j < n and not words[j].startswith("-"):
                j += 1
            return j
        return None
    if low in _PKG_RUN:
        j = _skip_opts(words, i + 1, {"--directory", "-C", "--file"})
        if j < n and words[j] in _PKG_RUN[low]:
            j = _skip_opts(words, j + 1, set())
            if j < n and words[j] == "--":
                j += 1
            return j
    return None


def invoked_programs(words):
    """Every program this line will run, including the one a runner wraps."""
    progs, i, steps, n = [], 0, 0, len(words)
    while i < n and steps < 8:
        steps += 1
        w = words[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            i += 1
            continue
        low = w.rsplit("/", 1)[-1].lower()
        progs.append(low)
        if low in WRAPPERS:
            nxt = _wrapper_next(words, i + 1, low)
            if nxt > i:
                i = nxt
                continue
            break
        inner = _runner_inner(words, i, low)
        if inner is not None and inner > i:
            i = inner
            continue
        break
    return progs


def shell_c_argument(prog, args):
    """The script given to `sh -c` / `bash -lc`, or None if this is not that form."""
    if (prog or "").lower() not in SHELLS:
        return None
    i, n = 0, len(args)
    while i < n:
        a = args[i]
        if a == "--":
            return None
        if a == "-c" or (a.startswith("-") and not a.startswith("--") and "c" in a[1:]):
            return args[i + 1] if i + 1 < n else None
        if a in ("-o", "+o", "--rcfile", "--init-file"):
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        return None
    return None


def _abs_lex(path, cwd):
    if not path or path == "-" or PLACEHOLDER in path:
        return ""
    p = os.path.expanduser(path)
    if not os.path.isabs(p):
        p = os.path.join(cwd or ".", p)
    return lexical_norm(p)


def _fetcher_outputs(name, args, redirs, cwd):
    out, i, n = [], 0, len(args)
    while i < n:
        a = args[i]
        if name == "curl" and a in ("-o", "--output") and i + 1 < n:
            out.append(args[i + 1]); i += 2; continue
        if name == "curl" and a.startswith("--output="):
            out.append(a.split("=", 1)[1]); i += 1; continue
        if name == "curl" and a.startswith("-o") and not a.startswith("--") and len(a) > 2:
            out.append(a[2:]); i += 1; continue
        if name in ("wget", "wget2") and a in ("-O", "--output-document") and i + 1 < n:
            out.append(args[i + 1]); i += 2; continue
        if name in ("wget", "wget2") and a.startswith("--output-document="):
            out.append(a.split("=", 1)[1]); i += 1; continue
        i += 1
    for op, target in redirs:
        if op in (">", ">|", "&>") and target and not target.startswith("&") and PLACEHOLDER not in target:
            out.append(target)
    paths = []
    for raw in out:
        if raw in ("-", "/dev/stdout", "/dev/stderr"):
            continue
        p = _abs_lex(raw, cwd)
        if p:
            paths.append(p)
    return paths


def _tee_files(args, cwd):
    files, i = [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            files.extend(x for x in args[i + 1:] if PLACEHOLDER not in x)
            break
        if a.startswith("-") or PLACEHOLDER in a:
            i += 1
            continue
        files.append(a)
        i += 1
    return [p for p in (_abs_lex(x, cwd) for x in files) if p]


def _executed_files(name, args):
    """Script files this program would execute. Inline `-c` / `-e` code is not a file."""
    name = (name or "").lower()
    if name in ("source", "."):
        return [a for a in args if a and not a.startswith("-") and PLACEHOLDER not in a]
    if name in SHELLS:
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--":
                return [args[i + 1]] if i + 1 < len(args) and PLACEHOLDER not in args[i + 1] else []
            if a.startswith("-") and not a.startswith("--") and "c" in a[1:]:
                return []
            if a.startswith("-"):
                if a in ("-o", "+o", "--rcfile", "--init-file"):
                    i += 2
                    continue
                i += 1
                continue
            return [a]
        return []
    if name in EXEC_INTERPRETERS:
        i = 0
        while i < len(args):
            a = args[i]
            if a.lower() in CODE_FLAGS or (a.startswith("-") and not a.startswith("--") and len(a) > 1 and a[1:2] in "cemrE"):
                return []
            if a.startswith("-"):
                i += 1
                continue
            return [a]
        return []
    return []


_SUBST_TOKEN_RE = re.compile(r"__BUILD_IT_SAFE_SUBST__\d+__")


def _body_download_files(body, table, cwd, seen):
    """Files this text writes with curl/wget or `tee` of a download.

    A substitution runs before the command that contains it, so its files
    count. A download later in the same list does not: `sh app.py && curl -o
    app.py URL` runs the file that is already there."""
    found = set()
    source_seen = False
    for c in split_commands(body or ""):
        blob = " ".join(c["words"]) + " " + " ".join(t for _, t in c["redirs"])
        for tok in _SUBST_TOKEN_RE.findall(blob):
            if tok in seen:
                continue
            seen.add(tok)
            found |= _body_download_files(table.get(tok, ""), table, cwd, seen)
        if not c.get("piped_from"):
            source_seen = False
        name, args = head_prog(c["words"])
        if name in FETCHERS:
            found.update(_fetcher_outputs(name, args, c["redirs"], cwd))
            source_seen = True
        elif source_seen and name == "tee":
            found.update(_tee_files(args, cwd))
    return found


def check_shell(command, cwd, project, cfg, depth=0):
    if not isinstance(command, str) or not command.strip():
        return
    if depth > 6:
        raise Block("pipe-to-shell", "this command nests shells too deeply to check safely.",
                    "Run the inner command directly, without another `sh -c`.")
    if CURL_PIPE_RE.search(command) or SHELL_SUBST_RE.search(command) or SHELL_C_RE.search(command):
        raise Block("pipe-to-shell", "piping a download straight into a shell runs code nobody has read.",
                    "Download the script to a file, show it to the human, and run it only after they approve; or use the project's package manager.")
    noheredoc, heredocs = extract_heredocs(command)
    outer, inner, subst_table = extract_substitutions(noheredoc)
    pieces = [outer] + inner
    if TEE_TO_SHELL_RE.search(command) and any(f in command.lower() for f in _FETCH_WORDS):
        raise Block("pipe-to-shell", "this sends a download into a shell through `>( … )`, so downloaded code would run without anyone reading it.",
                    "Download the script to a file, show it to the human, and run it only after they approve.")
    check_fetch_and_run(pieces, inner, [])
    progs_all = []
    subst_secret = []
    for body in inner:
        for c in split_commands(body):
            for w in c["words"][1:]:
                r = token_secret(w, cwd, cfg)
                if r:
                    subst_secret.append((w, r))
    nested = []
    for piece in pieces:
        cmds = split_commands(piece)
        downloaded = set()
        subst_seen = set()
        source_seen = False
        for k, c in enumerate(cmds):
            blob = " ".join(c["words"]) + " " + " ".join(t for _, t in c["redirs"])
            for tok in _SUBST_TOKEN_RE.findall(blob):
                if tok in subst_seen:
                    continue
                subst_seen.add(tok)
                # The substitution runs as this command is expanded, before it.
                downloaded |= _body_download_files(subst_table.get(tok, ""), subst_table, cwd, subst_seen)
            if not c.get("piped_from"):
                source_seen = False
            prog, cargs, _, _ = program_and_args(c["words"])
            progs_all.extend(invoked_programs(c["words"]))
            hname, hargs = head_prog(c["words"])
            for f in _executed_files(hname, hargs):
                if _abs_lex(f, cwd) in downloaded:
                    raise Block("pipe-to-shell",
                                "this downloads `%s` and runs it in the same command, so the code would run without anyone reading it." % os.path.basename(f),
                                "Download the script, show it to the human, and run it only after they approve.")
            if hname in FETCHERS:
                downloaded.update(_fetcher_outputs(hname, hargs, c["redirs"], cwd))
                source_seen = True
            elif source_seen and hname == "tee":
                downloaded.update(_tee_files(hargs, cwd))
            feeds_xargs = any(any(w.rsplit("/", 1)[-1] in ("xargs", "parallel") for w in x["words"][:3])
                              for x in cmds[k + 1:] if x.get("piped_from"))
            check_simple(c, cwd, project, cfg, {"heredocs": heredocs, "feeds_xargs": feeds_xargs,
                                                "subst_secret": subst_secret if piece is outer else []})
            # Kit files and hook configs: only reading tools may name them.
            git_sub = git_parts(cargs)[1] if prog == "git" else ""
            for w in cargs:
                if not is_kit_path(w, cwd, project):
                    continue
                if prog == "git" and git_sub in GIT_READ_SUBCMDS:
                    continue
                if prog != "git" and prog in READONLY_PROGS:
                    continue
                if prog in ("python", "python3", "sh", "bash") and cargs[:1] == [w]:
                    continue
                raise Block("kit-tamper", "agents may not change the Build It Safe Kit's files or, from the shell, the hook settings that run it (%s)." % w,
                            "Ask the human to change the kit.")
            script = shell_c_argument(prog, cargs)
            if script:
                nested.append(script)
    # A heredoc that merely mentions DROP DATABASE is not a database client.
    # The client may be behind a runner: `docker compose exec db psql`, `npm exec prisma`.
    if DB_DROP_RE.search(command) or DB_TOOL_RE.search(command):
        if any((p or "").lower() in DB_CLIENTS or (p or "").lower().startswith("redis") for p in progs_all):
            raise Block("destructive", "this command drops or resets a database. A dropped database is gone unless a backup restores it.",
                        "Ask the human. Never run this against production.")
    for script in nested:
        check_shell(script, cwd, project, cfg, depth + 1)


# --------------------------------------------------------------------------
# Rules for file writes
# --------------------------------------------------------------------------

FALLBACK_PATTERNS = [
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16}\b")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{60,}\b")),
    ("stripe-secret", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-(?:api|admin)\d\d-[A-Za-z0-9_-]{80,}\b")),
    ("openai-key", re.compile(r"\bsk-(?:proj|svcacct|admin)-[A-Za-z0-9_-]{40,}\b")),
    ("supabase-secret", re.compile(r"\bsb_secret_[A-Za-z0-9_-]{20,}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
]


def find_gitleaks():
    cand = os.environ.get("BUILD_IT_SAFE_GITLEAKS") or shutil.which("gitleaks")
    if cand:
        return cand
    for d in ("~/.local/bin", "/opt/homebrew/bin", "/usr/local/bin", "~/go/bin", "~/bin"):
        p = os.path.expanduser(os.path.join(d, "gitleaks"))
        if os.access(p, os.X_OK):
            return p
    return None


def scan_text(text, project):
    """Return a list of rule IDs for secrets found in text (never the values)."""
    if not text or len(text) < 8:
        return []
    data = text[:MAX_SCAN_BYTES]
    gl = find_gitleaks()
    if gl:
        cmd = [gl, "stdin", "--no-banner", "--redact", "--exit-code", "3", "--log-level", "error",
               "--report-format", "json", "--report-path", "-"]
        cfgfile = os.path.join(project, ".gitleaks.toml") if project else ""
        if cfgfile and os.path.isfile(cfgfile):
            cmd += ["--config", cfgfile]
        try:
            r = subprocess.run(cmd, input=data, capture_output=True, text=True, timeout=20,
                               cwd=project or None)
            if r.returncode in (0, 3):
                try:
                    found = json.loads(r.stdout or "[]")
                except ValueError:
                    found = []
                ids = sorted({f.get("RuleID", "secret") for f in found})
                if r.returncode == 3 and not ids:
                    ids = ["secret"]
                return ids
        except Exception:
            pass
    return sorted({name for name, rx in FALLBACK_PATTERNS if rx.search(data)})


def check_write(path, new_text, cwd, project, cfg, old_text=None, tool="Write"):
    if path and is_kit_path(path, cwd, project, configs=False):
        raise Block("kit-tamper", "agents may not change the Build It Safe Kit's own files (%s)." % path,
                    "Ask the human to change the kit.")
    check_protected(path, old_text, new_text, cwd, project, cfg, tool)
    reason = secret_reason(path, cfg, cwd) if path else None
    if reason and "environment" in reason:
        return  # secrets belong in .env (which must be gitignored)
    ids = scan_text(new_text, project)
    if ids:
        raise Block("secret-write", "the text written to %s contains what looks like a real key (%s)." % (
            os.path.basename(path) if path else "this file", ", ".join(ids)),
            "Put the key in .env (gitignored) or the host's secret store, and read it from an environment variable in code. Use a placeholder such as `YOUR_KEY_HERE` in examples.")


HOOK_CONFIG_FILES = (".claude/settings.json", ".claude/settings.local.json", ".cursor/hooks.json",
                     ".codex/hooks.json", ".gemini/settings.json", ".github/workflows/build-it-safe.yml",
                     ".pre-commit-config.yaml")


def check_protected(path, old_text, new_text, cwd, project, cfg, tool):
    if not path:
        return
    absp = os.path.normpath(path if os.path.isabs(path) else os.path.join(cwd, path))
    root = project or cwd
    rel = os.path.relpath(absp, root).replace("\\", "/")
    rules = []
    if rel in HOOK_CONFIG_FILES or rel.startswith(".github/hooks/"):
        rules.append(("build-it-safe", "the Build It Safe Kit's hook"))
    for entry in cfg.get("protected", []):
        if fnmatch.fnmatch(rel, entry.get("file", "")):
            for name in entry.get("names", []):
                rules.append((name, "`%s`" % name))
    if not rules:
        return
    if old_text is None and tool == "Write":
        try:
            with open(absp, "r", encoding="utf-8", errors="replace") as fh:
                old_text = fh.read(MAX_SCAN_BYTES)
        except OSError:
            return
    if old_text is None:
        return
    for name, label in rules:
        rx = re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")
        if len(rx.findall(old_text)) > len(rx.findall(new_text or "")):
            raise Block("protected-code", "this change to %s removes %s, which is on the protected list." % (rel, label),
                        "Keep it. If it truly must go, ask the human to update .build-it-safe/config.json first.")


def added_patch_lines(patch):
    files, added = [], []
    for line in patch.splitlines():
        m = re.match(r"^\*\*\* (?:Add|Update) File: (.+)$", line) or re.match(r"^\+\+\+ (?:b/)?(.+)$", line)
        if m:
            files.append(m.group(1).strip())
        elif line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    return files, "\n".join(added)


# --------------------------------------------------------------------------
# Payload handling
# --------------------------------------------------------------------------

SHELL_TOOLS = {"bash", "powershell", "run_shell_command", "shell", "exec_command", "local_shell",
               "terminal", "run_terminal_cmd", "runterminalcommand", "shellcommand"}
READ_TOOLS = {"read", "read_file", "read_many_files", "view", "notebookread", "readfile", "cat"}
WRITE_TOOLS = {"write", "write_file", "create", "createfile", "write_to_file", "notebookedit"}
EDIT_TOOLS = {"edit", "multiedit", "replace", "str_replace", "str_replace_editor", "edit_file",
              "editfile", "search_replace"}
SEARCH_TOOLS = {"grep", "search_file_content", "codebase_search"}   # read file contents
LIST_TOOLS = {"glob", "list_directory", "ls", "find_files"}          # list names only: allowed
PATH_KEYS = ("file_path", "absolute_path", "path", "filePath", "filepath", "notebook_path", "target_file", "file")


def find_project(cwd):
    env = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("GEMINI_PROJECT_DIR") or os.environ.get("CURSOR_PROJECT_DIR")
    if env and os.path.isdir(env):
        return os.path.realpath(env)
    d = os.path.realpath(cwd)
    while True:
        if os.path.isdir(os.path.join(d, ".build-it-safe")) or os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.realpath(cwd)
        d = parent


def load_config(project):
    try:
        with open(os.path.join(project, ".build-it-safe", "config.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
            return cfg if isinstance(cfg, dict) else {}
    except (OSError, ValueError):
        return {}


def normalize(payload):
    """Map any supported agent's payload to (tool_name, tool_input, cwd)."""
    cwd = payload.get("cwd") or os.getcwd()
    event = str(payload.get("hook_event_name") or payload.get("hookEventName") or "")
    if "tool_name" in payload:
        ti = payload.get("tool_input") or {}
        return str(payload["tool_name"]), ti if isinstance(ti, dict) else {"command": str(ti)}, cwd
    if "toolName" in payload:  # GitHub Copilot camelCase payload
        args = payload.get("toolArgs") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                args = {"command": args}
        return str(payload["toolName"]), args if isinstance(args, dict) else {}, cwd
    if event == "beforeShellExecution" or ("command" in payload and "file_path" not in payload):
        return "Bash", {"command": payload.get("command", "")}, cwd
    if event == "beforeReadFile" or "file_path" in payload:
        return "Read", {"file_path": payload.get("file_path", "")}, cwd
    return "", {}, cwd


def evaluate(payload):
    tool, ti, cwd = normalize(payload)
    if not os.path.isdir(cwd):
        cwd = os.getcwd()
    project = find_project(cwd)
    cfg = load_config(project)
    if cfg.get("guard_enabled") is False:
        return
    name = tool.lower()
    if name.startswith("mcp__") or name.startswith("mcp_"):
        name = "mcp"

    command = ti.get("command") or ti.get("cmd")
    if isinstance(command, list):
        parts = [str(c) for c in command]
        if len(parts) >= 3 and parts[0].rsplit("/", 1)[-1] in SHELLS and parts[1] in ("-c", "-lc", "-ic", "-lic"):
            command = parts[2]                    # Codex style: ["bash", "-lc", "<script>"]
        else:
            command = " ".join(parts)
    if name == "apply_patch" or (isinstance(command, str) and command.lstrip().startswith("*** Begin Patch")):
        files, added = added_patch_lines(command or ti.get("input", "") or ti.get("patch", ""))
        for f in files:
            check_write(f, added, cwd, project, cfg, old_text=None, tool="Patch")
        return
    if name in SHELL_TOOLS or (command and name not in READ_TOOLS | WRITE_TOOLS | EDIT_TOOLS):
        check_shell(command if isinstance(command, str) else "", cwd, project, cfg)
        if name in SHELL_TOOLS:
            return

    paths = []
    for k in PATH_KEYS:
        v = ti.get(k)
        if isinstance(v, str) and v:
            paths.append(v)
    for k in ("paths", "file_paths", "files"):
        v = ti.get(k)
        if isinstance(v, list):
            paths.extend(str(x) for x in v if isinstance(x, (str, bytes)))

    if name in LIST_TOOLS:
        return
    if name in READ_TOOLS or name in SEARCH_TOOLS or name not in WRITE_TOOLS | EDIT_TOOLS:
        for p in paths:
            r = secret_reason(p, cfg, cwd) or glob_reaches_secret(p, cwd, cfg)
            if r:
                raise Block("secret-read", "`%s` is %s. Agents must not read it." % (os.path.basename(p.rstrip("/")) or p, r),
                            "Read `.env.example` for variable names; the app loads the real file itself. Ask the human if you need a value checked.")
        if name in SEARCH_TOOLS:
            g = ti.get("glob") or ti.get("include")
            if isinstance(g, str) and g:
                r = secret_reason(g, cfg, cwd) or glob_reaches_secret(g, cwd, cfg)
                if r:
                    raise Block("secret-read", "the search pattern `%s` reaches secret files (%s)." % (g, r),
                                "Search source files only, or exclude .env files.")
        if name in READ_TOOLS or name in SEARCH_TOOLS:
            return

    path = paths[0] if paths else ""
    if name in WRITE_TOOLS:
        text = ti.get("content") or ti.get("new_source") or ti.get("file_text") or ti.get("text") or ""
        check_write(path, text if isinstance(text, str) else "", cwd, project, cfg, None, "Write")
        return
    if name in EDIT_TOOLS:
        edits = ti.get("edits") if isinstance(ti.get("edits"), list) else [ti]
        olds = "\n".join(str(e.get("old_string") or e.get("old_str") or "") for e in edits if isinstance(e, dict))
        news = "\n".join(str(e.get("new_string") or e.get("new_str") or e.get("content") or "") for e in edits if isinstance(e, dict))
        check_write(path, news, cwd, project, cfg, olds, "Edit")
        return
    if name == "mcp" or not name:
        texts = [v for v in ti.values() if isinstance(v, str) and len(v) >= 20]
        ids = scan_text("\n".join(texts), project) if texts else []
        if ids:
            raise Block("secret-write", "this tool call sends what looks like a real key (%s) to %s." % (", ".join(ids), tool or "a tool"),
                        "Never pass keys to tools or services in plain text.")


def main(argv):
    if len(argv) > 1 and argv[1] == "--version":
        print("build-it-safe guard v%s" % VERSION)
        return 0
    if len(argv) > 1 and argv[1] == "--scan-diff":
        # Fallback for the git hooks when gitleaks is missing: scan the added
        # lines of a unified diff on stdin with the built-in patterns.
        added = "\n".join(l[1:] for l in sys.stdin.read().splitlines()
                          if l.startswith("+") and not l.startswith("+++"))
        ids = sorted({n for n, rx in FALLBACK_PATTERNS if rx.search(added)})
        if ids:
            sys.stderr.write("build-it-safe: possible keys in this change (%s).\n" % ", ".join(ids))
            return 1
        return 0
    if len(argv) > 2 and argv[1] == "--check-command":
        payload = {"tool_name": "Bash", "tool_input": {"command": argv[2]}, "cwd": os.getcwd()}
    elif len(argv) > 2 and argv[1] == "--check-read":
        payload = {"tool_name": "Read", "tool_input": {"file_path": os.path.abspath(argv[2])}, "cwd": os.getcwd()}
    else:
        raw = sys.stdin.read()
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except ValueError:
            sys.stderr.write("build-it-safe guard: could not read the hook input, so the call was stopped to be safe.\n")
            return BLOCK
        if not isinstance(payload, dict):
            return 0
    try:
        evaluate(payload)
    except Block as b:
        msg = "BLOCKED by build-it-safe (%s): %s" % (b.rule, b.reason)
        if b.advice:
            msg += "\nInstead: " + b.advice
        sys.stderr.write(msg + "\n")
        return BLOCK
    except Exception as e:  # a bug in the guard must not silently allow everything
        sys.stderr.write("build-it-safe guard error (%s); the call was stopped to be safe. "
                         "A human can report this and set \"guard_enabled\": false in .build-it-safe/config.json.\n"
                         % type(e).__name__)
        return BLOCK
    if len(argv) > 2:
        print("allowed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
