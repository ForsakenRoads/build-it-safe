#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Build It Safe, Forsaken Roads® (https://github.com/ForsakenRoads/build-it-safe). See NOTICE.
"""build-it-safe hidden-text check: invisible characters in agent rules files.

Invisible Unicode can hide instructions that a person reviewing a file never
sees but an AI agent reads (the "Rules File Backdoor", Pillar Security, 2025).
This check looks for:
  * Unicode tag characters (U+E0000-U+E007F), which can spell hidden ASCII text;
  * bidirectional controls (U+202A-U+202E, U+2066-U+2069, U+200E/F, U+061C),
    the "Trojan Source" characters;
  * zero-width and other invisible format characters (category Cf), and
    variation selectors outside emoji.

It wraps anti-trojan-source (Apache-2.0, Liran Tal) when that tool is
installed, and otherwise uses the same character classes from Python's own
Unicode tables. Emoji joiners and emoji variation selectors are not reported.

Usage:
  hidden_text.py [FILE ...]      scan the given files
  hidden_text.py --staged        scan staged agent rules files (git pre-commit)
  hidden_text.py --rules         scan every agent rules file in the repository
  hidden_text.py --all-text      with --staged or --rules: scan all text files
Exit code 1 when anything is found, 0 when clean.
"""

import fnmatch
import json
import os
import shutil
import subprocess
import sys
import unicodedata

RULES_GLOBS = (
    "AGENTS.md", "*/AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "*/CLAUDE.md",
    "CLAUDE.local.md", "GEMINI.md", "*/GEMINI.md", ".cursorrules", ".windsurfrules",
    ".clinerules", ".clinerules/*", ".github/copilot-instructions.md",
    ".github/instructions/*", ".github/prompts/*", ".github/agents/*", ".github/hooks/*",
    ".cursor/*", ".claude/*", ".agents/*", ".codex/*", ".gemini/*", ".windsurf/*",
    "*SKILL.md", ".mcp.json", ".vscode/settings.json", ".vscode/mcp.json",
    ".build-it-safe/*",
    "*skills/*",                     # every file of a skill, reference pages included
    "*/core/security-block.md",      # the kit's own rules block
    "*agent-rules*.md",              # the manual's chapter on agent rules
)
BIDI = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A)) | {0x200E, 0x200F, 0x061C}
VS = set(range(0xFE00, 0xFE10)) | set(range(0xE0100, 0xE01F0))
EXTRA_INVISIBLE = {0x115F, 0x1160, 0x3164, 0xFFA0, 0x034F, 0x180E, 0x2800}


def is_rules_file(path):
    p = path.replace("\\", "/")
    return any(fnmatch.fnmatch(p, g) for g in RULES_GLOBS)


def is_emojiish(ch):
    if not ch:
        return False
    cp = ord(ch)
    return unicodedata.category(ch) == "So" or 0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF \
        or cp in (0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139, 0x3030, 0x303D, 0x20E3)


def emoji_context(line, col):
    """True if the character at col is a joiner/selector inside an emoji sequence."""
    ch = line[col]
    cp = ord(ch)
    prev = line[col - 1] if col > 0 else ""
    nxt = line[col + 1] if col + 1 < len(line) else ""
    if cp in (0xFE0E, 0xFE0F):
        return is_emojiish(prev) or prev.isdigit() or prev in "#*"
    if cp == 0x200D:
        return (is_emojiish(prev) or ord(prev or "a") in (0xFE0F,)) and (is_emojiish(nxt) or 0x2640 <= ord(nxt or "a") <= 0x2642)
    if 0xE0020 <= cp <= 0xE007F:
        # Subdivision flags (England, Scotland, Wales) use tags after U+1F3F4.
        j = col
        while j > 0 and 0xE0020 <= ord(line[j - 1]) <= 0xE007F:
            j -= 1
        return j > 0 and ord(line[j - 1]) == 0x1F3F4
    return False


def classify(cp, ch):
    if 0xE0000 <= cp <= 0xE007F:
        return "tag character (can hide text)"
    if cp in BIDI:
        return "bidirectional control"
    if cp in VS:
        return "variation selector"
    if cp in EXTRA_INVISIBLE:
        return "invisible letter"
    cat = unicodedata.category(ch)
    if cat == "Cf":
        return "invisible format character"
    if cat == "Cc" and ch not in "\t\n\r":
        return "control character"
    if cat in ("Co", "Cn") and cp > 0xFFFF:
        return "unassigned or private-use character"
    return None


def scan_text(text):
    findings = []
    for ln, line in enumerate(text.split("\n"), 1):
        for col, ch in enumerate(line):
            cp = ord(ch)
            if cp < 0x80 and ch not in "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x1b\x7f":
                continue
            if cp == 0xFEFF and ln == 1 and col == 0:
                continue  # byte-order mark at the start of a file
            kind = classify(cp, ch)
            if kind and not emoji_context(line, col):
                findings.append((ln, col + 1, cp, kind))
    return findings


def scan_with_ats(files):
    """Use anti-trojan-source when installed; return {file: [(line, col, cp, kind)]} or None."""
    exe = shutil.which("anti-trojan-source")
    local = os.path.join("node_modules", ".bin", "anti-trojan-source")
    if not exe and os.access(local, os.X_OK):
        exe = local
    if not exe or os.environ.get("BUILD_IT_SAFE_NO_ATS"):
        return None
    try:
        r = subprocess.run([exe, "--json"] + files, capture_output=True, text=True, timeout=120)
        data = json.loads(r.stdout or "[]")
    except Exception:
        return None
    out = {}
    for entry in data if isinstance(data, list) else []:
        f = entry.get("file")
        try:
            lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
        except OSError:
            lines = []
        for fd in entry.get("findings", []):
            ln, col = int(fd.get("line", 0)), int(fd.get("column", 0))
            try:
                cp = int(str(fd.get("codePoint", "U+0")).replace("U+", ""), 16)
            except ValueError:
                cp = 0
            line = lines[ln - 1] if 0 < ln <= len(lines) else ""
            idx = next((i for i, c in enumerate(line) if ord(c) == cp and i >= col - 2), -1)
            if idx >= 0 and emoji_context(line, idx):
                continue
            out.setdefault(f, []).append((ln, col, cp, fd.get("name", "hidden character")))
    return out


def git_files(staged):
    if staged:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]
    else:
        cmd = ["git", "ls-files", "-z"]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=30)
        return [f for f in r.stdout.decode("utf-8", "replace").split("\0") if f]
    except Exception:
        return []


def read_text(path, staged):
    try:
        if staged:
            r = subprocess.run(["git", "show", ":" + path], capture_output=True, timeout=30)
            data = r.stdout
        else:
            with open(path, "rb") as fh:
                data = fh.read(5_000_000)
    except Exception:
        return None
    if b"\0" in data[:8192]:
        return None  # binary
    return data.decode("utf-8", "replace")


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    staged = "--staged" in flags
    if staged or "--rules" in flags:
        files = git_files(staged)
        if "--all-text" not in flags:
            files = [f for f in files if is_rules_file(f)]
        files += [a for a in args if a not in files]
    else:
        files = args
    if not files:
        return 0
    results = {}
    ats = None if staged else scan_with_ats([f for f in files if os.path.isfile(f)])
    if ats is not None:
        results = ats
    else:
        for f in files:
            text = read_text(f, staged)
            if text is None:
                continue
            found = scan_text(text)
            if found:
                results[f] = found
    if not results:
        return 0
    total = sum(len(v) for v in results.values())
    sys.stderr.write("build-it-safe: hidden characters found in %d file(s), %d in all.\n" % (len(results), total))
    for f, found in sorted(results.items()):
        for ln, col, cp, kind in found[:20]:
            name = unicodedata.name(chr(cp), "") if cp else ""
            sys.stderr.write("  %s:%d:%d  U+%04X %s (%s)\n" % (f, ln, col, cp, name, kind))
        if len(found) > 20:
            sys.stderr.write("  %s: ... and %d more\n" % (f, len(found) - 20))
    sys.stderr.write("These characters are invisible to people but readable by AI agents. Open the file in an editor that shows\n"
                     "hidden characters, remove them, and check where the text came from.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
