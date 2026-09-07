from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


def inline_markup(value: str) -> str:
    escaped = html.escape(value, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^\s)]+)\)",
        lambda match: '<a href="' + html.escape(
            html.unescape(match[2]), quote=True
        ) + '">' + match[1] + '</a>',
        escaped,
    )
    return escaped


def markdown_to_html(markdown: str, title: str) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    list_open = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline_markup(' '.join(line.strip() for line in paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_open
        if list_open:
            output.append("</ul>")
            list_open = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            flush_paragraph()
            close_list()
            continue
        if line.startswith("# "):
            flush_paragraph()
            close_list()
            output.append(f"<h1>{inline_markup(line[2:])}</h1>")
            continue
        if line.startswith("## "):
            flush_paragraph()
            close_list()
            output.append(f"<h2>{inline_markup(line[3:])}</h2>")
            continue
        if line.startswith("### "):
            flush_paragraph()
            close_list()
            output.append(f"<h3>{inline_markup(line[4:])}</h3>")
            continue
        if line.startswith("- "):
            flush_paragraph()
            if not list_open:
                output.append("<ul>")
                list_open = True
            output.append(f"<li>{inline_markup(line[2:])}</li>")
            continue
        if line.startswith("| ") or line.startswith("|---"):
            flush_paragraph()
            close_list()
            output.append(f"<p class=table-row>{inline_markup(line)}</p>")
            continue
        paragraph.append(line)

    flush_paragraph()
    close_list()
    body = "\n".join(output)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
@page {{ size: A4; margin: 18mm 17mm 18mm 17mm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: Arial, Helvetica, sans-serif; color: #1d2024; font-size: 10.5pt; line-height: 1.42; }}
h1 {{ font-size: 22pt; margin: 0 0 14pt; color: #172a45; page-break-after: avoid; }}
h2 {{ font-size: 14pt; margin: 18pt 0 7pt; color: #1e4f75; page-break-after: avoid; }}
h3 {{ font-size: 11.5pt; margin: 13pt 0 5pt; color: #1e4f75; page-break-after: avoid; }}
p {{ margin: 0 0 8pt; orphans: 3; widows: 3; }}
ul {{ margin: 0 0 9pt 18pt; padding: 0; }}
li {{ margin: 0 0 4pt; }}
code {{ font-family: Consolas, monospace; font-size: 9pt; background: #f0f3f6; padding: 1pt 3pt; }}
.table-row {{ font-family: Consolas, monospace; font-size: 8.5pt; white-space: pre-wrap; margin-bottom: 2pt; }}
.cover {{ border-bottom: 1.5pt solid #1e4f75; margin-bottom: 18pt; padding-bottom: 9pt; }}
.meta {{ color: #59636e; font-size: 9pt; }}
</style>
</head>
<body>
<div class="cover"><div class="meta">Working submission dossier \u00b7 2027</div></div>
{body}
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("html_output", type=Path)
    parser.add_argument("--title", default="Dimensiones del Orden")
    args = parser.parse_args()
    content = args.source.read_text(encoding="utf-8")
    rendered = markdown_to_html(content, args.title)
    args.html_output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
