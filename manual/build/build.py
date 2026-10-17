#!/usr/bin/env python3
"""Build the manual: Markdown sources -> one HTML file -> PDF (WeasyPrint) and EPUB (pandoc).

Run from anywhere:  python3 manual/build/build.py [--pdf-only | --epub-only]

What the preprocessing step does, so the sources stay plain Markdown:
  {{TITLE}}, {{MAIN_TITLE}}, {{SUBTITLE}}, {{AUTHOR}}, {{HANDLE}},
  {{ATTRIBUTION}}, {{ATTRIBUTION_NOTE}}             replaced from book.toml
  ## Heading {#ch-id}       in a numbered file gets "N. " in front (chapters run 1..N)
  {{ch:ch-id}}              becomes a link "chapter N"; {{Ch:ch-id}} gives "Chapter N"
  [[key]] or [[a; b]]       becomes numbered source notes that link to the Sources appendix
  - **[key]** text          in 95-sources.md: the source registry, renumbered in citation order
  ![Caption](images/x.png)  gets "Figure N." and, if the file is missing, a marked placeholder

Intermediates go to <worktree>/_regen/ (it holds a CACHEDIR.TAG). Outputs go to manual/dist/.
"""
import html
import re
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

BUILD = Path(__file__).resolve().parent
MANUAL = BUILD.parent
SRC = MANUAL / "src"
DIST = MANUAL / "dist"
REGEN = MANUAL.parent / "_regen" / "manual-build"

CITE = re.compile(r"[ \t]*\[\[([a-z0-9][a-z0-9-]*(?:\s*;\s*[a-z0-9][a-z0-9-]*)*)\]\]")
SOURCE_LINE = re.compile(r"^- \*\*\[([a-z0-9][a-z0-9-]*)\]\*\* (.+)$")
CHAPTER = re.compile(r"^## (?!.*\.unnumbered)(.+?)\s*\{#(ch-[a-z0-9-]+)([^}]*)\}\s*$")
CHREF = re.compile(r"\{\{([Cc])h:(ch-[a-z0-9-]+)\}\}")
FIGURE = re.compile(r"^!\[(.+)\]\(([^)\s]+)\)(\{[^}]*\})?\s*$")


def fail(msg):
    sys.exit(f"build: ERROR: {msg}")


def load_config():
    with open(BUILD / "book.toml", "rb") as f:
        cfg = tomllib.load(f)
    main, _, sub = cfg["title"].partition(": ")
    cfg["main_title"], cfg["subtitle"] = main, sub
    return cfg


def placeholder_svg(path, caption):
    """A dashed box that says plainly that the screenshot is still to come."""
    words, lines, line = caption.split(), [], ""
    for w in words:
        if len(line) + len(w) > 70:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    lines.append(line)
    text = "".join(
        f'<text x="400" y="{150 + 26 * i}" font-size="17" text-anchor="middle">{html.escape(t)}</text>'
        for i, t in enumerate(lines[:5]))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" width="800" height="300">
<rect x="6" y="6" width="788" height="288" rx="10" fill="#f6f6f2" stroke="#9a3b1b" stroke-width="3" stroke-dasharray="14 8"/>
<g font-family="Noto Sans, DejaVu Sans, sans-serif" fill="#333">
<text x="400" y="70" font-size="26" font-weight="700" text-anchor="middle" fill="#9a3b1b">SCREENSHOT PLACEHOLDER</text>
<text x="400" y="108" font-size="16" text-anchor="middle" font-family="Noto Sans Mono, DejaVu Sans Mono, monospace">{html.escape(path.name)}</text>
{text}
</g></svg>"""
    out = REGEN / "placeholders" / (path.stem + ".svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    return out


def preprocess(cfg):
    files = sorted(p for p in SRC.glob("*.md") if re.match(r"\d\d-", p.name))
    if not files:
        fail(f"no sources in {SRC}")
    texts = {p.name: p.read_text(encoding="utf-8") for p in files}

    # Pass 1: chapter numbers (only files 10-89 carry numbered chapters).
    chapters, n = {}, 0
    for name, text in texts.items():
        if not ("10" <= name[:2] <= "89"):
            continue
        for line in text.splitlines():
            m = CHAPTER.match(line)
            if m:
                n += 1
                chapters[m.group(2)] = n

    # The source registry lives in 95-sources.md.
    reg_name = next((k for k in texts if k.startswith("95-")), None)
    if not reg_name:
        fail("95-sources.md is missing")
    registry = {}
    for line in texts[reg_name].splitlines():
        m = SOURCE_LINE.match(line)
        if m:
            if m.group(1) in registry:
                fail(f"source key [{m.group(1)}] is defined twice")
            registry[m.group(1)] = m.group(2)

    numbers, figures, missing_images = {}, 0, []

    def cite(m):
        keys = [k.strip() for k in m.group(1).split(";")]
        parts = []
        for k in keys:
            if k not in registry:
                fail(f"citation [[{k}]] has no entry in {reg_name}")
            if k not in numbers:
                numbers[k] = len(numbers) + 1
            parts.append(f"[{numbers[k]}](#src-{numbers[k]})")
        return "[" + ", ".join(parts) + "]{.cite}"

    def chref(m):
        cid = m.group(2)
        if cid not in chapters:
            fail(f"cross-reference to unknown chapter {cid}")
        word = "Chapter" if m.group(1) == "C" else "chapter"
        return f"[{word} {chapters[cid]}](#{cid})"

    out = []
    for name, text in texts.items():
        if name == reg_name:
            continue  # rendered last, once every citation is numbered
        for key, val in (("{{TITLE}}", cfg["title"]), ("{{MAIN_TITLE}}", cfg["main_title"]),
                         ("{{SUBTITLE}}", cfg["subtitle"]), ("{{AUTHOR}}", cfg["author"]),
                         ("{{HANDLE}}", cfg["handle"]),
                         ("{{ATTRIBUTION}}", cfg["attribution"].replace("*", "\\*")),
                         ("{{ATTRIBUTION_NOTE}}", cfg["attribution_note"].replace("*", "\\*"))):
            text = text.replace(key, val)
        lines, in_code = [], False
        for line in text.splitlines():
            if line.startswith("```"):
                in_code = not in_code
            if in_code:
                lines.append(line)
                continue
            m = CHAPTER.match(line)
            if m and "10" <= name[:2] <= "89":
                line = f"## {chapters[m.group(2)]}. {m.group(1)} {{#{m.group(2)}{m.group(3)}}}"
            fm = FIGURE.match(line)
            if fm:
                figures += 1
                caption, target, attrs = fm.group(1), fm.group(2), fm.group(3) or ""
                img = MANUAL / target
                if not img.exists():
                    missing_images.append(target)
                    target = str(placeholder_svg(img, caption))
                    caption += " *(Placeholder: the screenshot is still to come.)*"
                line = f"![Figure {figures}. {caption}]({target}){attrs}"
            line = CITE.sub(cite, line)
            line = CHREF.sub(chref, line)
            lines.append(line)
        out.append("\n".join(lines))

    # The Sources appendix: the registry's intro text, then the numbered list.
    reg_lines, entries_done = [], False
    by_number = sorted(numbers.items(), key=lambda kv: kv[1])
    for line in texts[reg_name].splitlines():
        if SOURCE_LINE.match(line):
            if not entries_done:
                for key, num in by_number:
                    entry = CHREF.sub(chref, registry[key])
                    reg_lines.append(f"::: {{.source}}\n[{num}.]{{#src-{num} .srcnum}} {entry}\n:::\n")
                entries_done = True
            continue
        reg_lines.append(line)
    out.append("\n".join(reg_lines))

    unused = sorted(set(registry) - set(numbers))
    return "\n\n".join(out) + "\n", chapters, numbers, unused, missing_images


def fix_epub_svg_names(epub):
    """pandoc names plain SVG files *.svgz; some readers then try to unzip them. Rename to *.svg."""
    tmp = epub.with_suffix(".tmp")
    with zipfile.ZipFile(epub) as zin, zipfile.ZipFile(tmp, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            name = item.filename
            if name.endswith(".svgz") and not data.startswith(b"\x1f\x8b"):
                name = name[:-1]
            if name.endswith((".xhtml", ".opf", ".ncx")):
                data = re.sub(rb"(media/file\d+\.svg)z", rb"\1", data)
            mode = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
            zout.writestr(zipfile.ZipInfo(name, item.date_time), data, compress_type=mode)
    tmp.replace(epub)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        fail(f"{cmd[0]} failed:\n{r.stderr}")
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)


def main():
    want_pdf = "--epub-only" not in sys.argv
    want_epub = "--pdf-only" not in sys.argv
    cfg = load_config()
    REGEN.mkdir(parents=True, exist_ok=True)
    tag = REGEN.parent / "CACHEDIR.TAG"
    if not tag.exists():
        tag.write_text("Signature: 8a477f597d28d172789f06886806bc55\n# Regenerable build intermediates.\n")
    DIST.mkdir(parents=True, exist_ok=True)

    book, chapters, numbers, unused, missing = preprocess(cfg)
    md = REGEN / "book.md"
    md.write_text(book, encoding="utf-8")

    meta = ["-M", f"title={cfg['main_title']}", "-M", f"subtitle={cfg['subtitle']}",
            "-M", f"author={cfg['author']}", "-M", f"lang={cfg['language']}",
            "-M", f"edition={cfg['edition']}", "-M", f"fulltitle={cfg['title']}",
            "-M", f"handle={cfg['handle']}", "-M", f"attribution={cfg['attribution']}",
            "-M", f"attribution-note={cfg['attribution_note']}"]
    common = ["pandoc", str(md), "--from", "markdown+fenced_divs+bracketed_spans-tex_math_dollars",
              "--resource-path", str(MANUAL), "--toc", "--toc-depth=2", "--wrap=none", "--no-highlight", *meta]

    if want_pdf:
        out_html = REGEN / "book.html"
        run([*common, "--to", "html5", "--standalone", "--template", str(BUILD / "template.html"),
             "--css", str(BUILD / "book.css"), "--output", str(out_html)])
        pdf = DIST / cfg["pdf"]
        run(["weasyprint", "--base-url", str(MANUAL), "--pdf-variant", "pdf/ua-1", str(out_html), str(pdf)])
        print(f"PDF:  {pdf}")
    if want_epub:
        epub = DIST / cfg["epub"]
        run([*common, "--to", "epub3", "--split-level=2", "--css", str(BUILD / "epub.css"),
             "--epub-title-page=true", "--output", str(epub)])
        fix_epub_svg_names(epub)
        print(f"EPUB: {epub}")

    print(f"chapters: {len(chapters)}  sources cited: {len(numbers)}")
    if unused:
        print("WARNING: sources never cited (not printed): " + ", ".join(unused), file=sys.stderr)
    if missing:
        print("placeholders used for: " + ", ".join(missing))


if __name__ == "__main__":
    main()
