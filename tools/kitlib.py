"""Shared code for the Build It Safe Kit's `install` and `doctor` (Python 3.8+ stdlib only)."""

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys

KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT_VERSION = 1
RUNTIME = ".build-it-safe"
MANIFEST = RUNTIME + "/manifest.json"
GUARD_REF = "build-it-safe/guard.py"

MD_BEGIN = "<!-- build-it-safe:begin v%d -->"
MD_END = "<!-- build-it-safe:end -->"
SH_BEGIN = "# build-it-safe:begin v%d"
SH_END = "# build-it-safe:end"
BEGIN_RE = {
    "md": re.compile(r"<!-- build-it-safe:begin v(\d+) -->"),
    "sh": re.compile(r"^# build-it-safe:begin v(\d+)[ \t]*$", re.M),
}
END_TEXT = {"md": MD_END, "sh": SH_END}

AGENT_NAMES = {
    "claude": "Claude Code", "codex": "Codex", "cursor": "Cursor",
    "copilot": "GitHub Copilot", "gemini": "Gemini CLI",
}
FRAMEWORK_DEPS = {
    "next": "Next.js", "vite": "Vite", "react-scripts": "Create React App", "expo": "Expo",
    "nuxt": "Nuxt", "@sveltejs/kit": "SvelteKit", "astro": "Astro",
    "@supabase/supabase-js": "Supabase", "@supabase/ssr": "Supabase", "firebase": "Firebase",
    "firebase-admin": "Firebase", "stripe": "Stripe", "@stripe/stripe-js": "Stripe",
}
PY_DEPS = {"django": "Django", "flask": "Flask", "fastapi": "FastAPI", "streamlit": "Streamlit",
           "supabase": "Supabase", "stripe": "Stripe", "firebase-admin": "Firebase"}


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def kit_path(*parts):
    return os.path.join(KIT_ROOT, *parts)


def read(path):
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def write(path, text, executable=False):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    if executable:
        mode = os.stat(path).st_mode
        os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(target, *args, check=False):
    try:
        r = subprocess.run(["git"] + list(args), cwd=target, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if check and r.returncode != 0:
        return None
    return r


def git_out(target, *args):
    r = git(target, *args)
    return r.stdout.strip() if r is not None and r.returncode == 0 else ""


def is_git_repo(target):
    return git_out(target, "rev-parse", "--is-inside-work-tree") == "true"


def which(name):
    return shutil.which(name)


def use_color(stream=sys.stdout):
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(stream, "isatty") and stream.isatty()


def wrap(text, indent, first="", lead=None):
    """Wrap to the terminal width with a hanging indent. `lead` is how many
    characters are printed before the text on its first line (default: indent)."""
    import textwrap
    width = max(60, min(shutil.get_terminal_size((100, 24)).columns, 140) - 2)
    lead = len(first) if first else (indent if lead is None else lead)
    out = textwrap.fill(text, width=width, initial_indent="\0" * lead, subsequent_indent=" " * indent,
                        break_on_hyphens=False, break_long_words=False)
    return (first or "") + out[lead:]


class Paint:
    def __init__(self, on):
        self.on = on

    def _c(self, code, s):
        return "\033[%sm%s\033[0m" % (code, s) if self.on else s

    def green(self, s): return self._c("32", s)
    def red(self, s): return self._c("31", s)
    def yellow(self, s): return self._c("33", s)
    def bold(self, s): return self._c("1", s)
    def dim(self, s): return self._c("2", s)
    def cyan(self, s): return self._c("36", s)


# --------------------------------------------------------------------------
# Marked blocks
# --------------------------------------------------------------------------

def find_block(text, style):
    """Return (start, end, version) of the kit's block, end exclusive of the newline after it."""
    if not text:
        return None
    m = BEGIN_RE[style].search(text)
    if not m:
        return None
    end_text = END_TEXT[style]
    e = text.find(end_text, m.end())
    if e == -1:
        return None
    e += len(end_text)
    if text[e:e + 1] == "\n":
        e += 1
    return m.start(), e, int(m.group(1))


def wrap_block(body, style):
    begin = (MD_BEGIN if style == "md" else SH_BEGIN) % KIT_VERSION
    body = body.strip("\n")
    return "%s\n%s\n%s\n" % (begin, body, END_TEXT[style])


def core_block():
    """The core block file already carries its markers; return it normalised."""
    text = read(kit_path("kit", "core", "security-block.md")) or ""
    return text.strip("\n") + "\n"


def upsert_block(text, block, style, position="end"):
    """Insert or replace the kit's block. The user's own text is never changed."""
    found = find_block(text or "", style)
    if found:
        s, e, _ = found
        return text[:s] + block + text[e:]
    text = text or ""
    if position == "after-shebang" and text.startswith("#!"):
        nl = text.find("\n")
        if nl == -1:
            return text + "\n" + block
        return text[:nl + 1] + block + text[nl + 1:]
    if position == "top":
        return block + ("\n" + text if text and not text.startswith("\n") else text)
    if text and not text.endswith("\n"):
        text += "\n"
    sep = "\n" if text.strip() else ""
    return text + sep + block


def remove_block(text, style):
    found = find_block(text or "", style)
    if not found:
        return text
    s, e, _ = found
    before, after = text[:s], text[e:]
    # Undo the blank line upsert_block added, so the file returns to what it was.
    if after == "" and before.endswith("\n\n"):
        before = before[:-1]
    elif before == "" and after.startswith("\n"):
        after = after[1:]
    return before + after


# --------------------------------------------------------------------------
# Detection
# --------------------------------------------------------------------------

def load_json(path):
    t = read(path)
    if t is None:
        return None, "missing"
    try:
        return json.loads(t), "ok"
    except ValueError:
        return None, "invalid"


def detect(target, agents_override=None):
    j = lambda *p: os.path.join(target, *p)
    ex = lambda *p: os.path.exists(j(*p))
    agents = set()
    if agents_override is not None:
        agents = set(a for a in agents_override if a in AGENT_NAMES)
    else:
        if ex("CLAUDE.md") or ex(".claude") or ex("CLAUDE.local.md") or which("claude"):
            agents.add("claude")
        if ex(".codex") or which("codex"):
            agents.add("codex")
        if ex(".cursor") or ex(".cursorrules") or which("cursor") or which("cursor-agent"):
            agents.add("cursor")
        if ex(".github", "copilot-instructions.md") or ex(".github", "instructions") or \
                ex(".github", "hooks") or which("copilot"):
            agents.add("copilot")
        if ex("GEMINI.md") or ex(".gemini") or which("gemini"):
            agents.add("gemini")

    frameworks, ecosystems = set(), set()
    pkg, _ = load_json(j("package.json"))
    if isinstance(pkg, dict):
        ecosystems.add("npm")
        deps = {}
        for k in ("dependencies", "devDependencies", "peerDependencies"):
            if isinstance(pkg.get(k), dict):
                deps.update(pkg[k])
        for dep, name in FRAMEWORK_DEPS.items():
            if dep in deps:
                frameworks.add(name)
    pytext = ""
    for f in ("requirements.txt", "pyproject.toml", "Pipfile", "setup.py", "setup.cfg"):
        t = read(j(f))
        if t is not None:
            ecosystems.add("pip")
            pytext += t.lower() + "\n"
    for dep, name in PY_DEPS.items():
        if re.search(r"(^|[\s\"'\[,])%s([\s\"'=<>~!\[,;]|$)" % re.escape(dep), pytext, re.M):
            frameworks.add(name)
    if ex("supabase"):
        frameworks.add("Supabase")
    if ex("firebase.json"):
        frameworks.add("Firebase")
    if ex("vercel.json") or ex(".vercel"):
        frameworks.add("Vercel")
    if ex("netlify.toml"):
        frameworks.add("Netlify")
    if ex("wrangler.toml") or ex("wrangler.jsonc") or ex("wrangler.json"):
        frameworks.add("Cloudflare Workers")
    if ex("go.mod"):
        ecosystems.add("gomod")
    if ex("Cargo.toml"):
        ecosystems.add("cargo")
    if ex("Gemfile"):
        ecosystems.add("bundler")

    gitrepo = is_git_repo(target)
    remotes = git_out(target, "remote", "-v") if gitrepo else ""
    github = ex(".github") or "github.com" in remotes
    return {
        "agents": agents,
        "frameworks": frameworks,
        "ecosystems": ecosystems,
        "git": gitrepo,
        "github": github,
        "precommit": ex(".pre-commit-config.yaml"),
        "husky": ex(".husky"),
    }


def tracked_secret_files(target):
    """Tracked files whose names say they hold secrets (contents are never opened)."""
    guard = load_guard()
    out = git_out(target, "ls-files", "-z")
    files = [f for f in out.split("\0") if f]
    hits = []
    for f in files:
        if f.startswith(RUNTIME + "/"):
            continue
        r = guard.secret_reason(f, {}, target)
        if r:
            hits.append((f, r))
    return hits


_GUARD = None


def load_guard():
    global _GUARD
    if _GUARD is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_it_safe_guard", kit_path("kit", "guard", "guard.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _GUARD = mod
    return _GUARD


# --------------------------------------------------------------------------
# Git hooks placement
# --------------------------------------------------------------------------

def hooks_placement(target):
    """Decide where the kit's git hooks go. Returns a dict describing the choice."""
    if not is_git_repo(target):
        return {"mode": "none", "why": "not a git repository"}
    root = os.path.realpath(git_out(target, "rev-parse", "--show-toplevel") or target)
    if os.path.exists(os.path.join(root, ".pre-commit-config.yaml")):
        return {"mode": "precommit", "why": "the repository uses the pre-commit framework"}
    hp = git_out(target, "config", "--get", "core.hooksPath")
    scope = git_out(target, "config", "--show-scope", "--get", "core.hooksPath").split("\t")[0] if hp else ""
    kit_dir = os.path.join(root, RUNTIME, "git-hooks")
    if hp:
        abs_hp = os.path.realpath(os.path.expanduser(hp) if os.path.isabs(os.path.expanduser(hp))
                                  else os.path.join(root, hp))
        if abs_hp == os.path.realpath(kit_dir):
            return {"mode": "kitdir", "dir": kit_dir, "scope": scope, "why": "core.hooksPath already points at the kit"}
        if abs_hp == root or abs_hp.startswith(root + os.sep):
            d = abs_hp
            if os.path.basename(abs_hp) == "_" and os.path.basename(os.path.dirname(abs_hp)) == ".husky":
                d = os.path.dirname(abs_hp)
            return {"mode": "blocks", "dir": d, "why": "core.hooksPath is %s" % hp}
        return {"mode": "kitdir-set", "dir": kit_dir, "prev": hp, "scope": scope,
                "why": "core.hooksPath (%s config) points outside this repository" % (scope or "global")}
    d = git_out(target, "rev-parse", "--git-path", "hooks")
    d = d if os.path.isabs(d) else os.path.join(root, d)
    return {"mode": "blocks", "dir": os.path.realpath(d), "why": "git's default hooks folder"}


def hook_block(name):
    """The lines the kit adds to a git hook file. If a branch predates the kit
    (no .build-it-safe/ there), the check is skipped with a warning instead of
    making every commit on that branch fail."""
    head = ('BUILD_IT_SAFE_HOOK="$(git rev-parse --show-toplevel)/.build-it-safe/git-hooks/%s"\n' % name)
    missing = ('echo "build-it-safe: $BUILD_IT_SAFE_HOOK is missing on this branch, so the %s scan was skipped." >&2' % name)
    if name == "pre-commit":
        body = head + ('if [ -x "$BUILD_IT_SAFE_HOOK" ]; then "$BUILD_IT_SAFE_HOOK" "$@" || exit 1; else %s; fi' % missing)
    else:
        body = (head + "BUILD_IT_SAFE_STDIN=$(cat)\n"
                'if [ -x "$BUILD_IT_SAFE_HOOK" ]; then\n'
                '  printf \'%s\\n\' "$BUILD_IT_SAFE_STDIN" | "$BUILD_IT_SAFE_HOOK" "$@" || exit 1\n'
                "else\n  " + missing + "\nfi\n"
                "exec <<BUILD_IT_SAFE_EOF\n$BUILD_IT_SAFE_STDIN\nBUILD_IT_SAFE_EOF")
    return wrap_block(body, "sh")
