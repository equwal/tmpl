#!/usr/bin/env python3
"""Convert template files with <++> placeholders to LuaSnip VSCode-format snippets.

Each language directory becomes one <lang>.json file. A package.json lists
them so the LuaSnip from_vscode loader can find them.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Map from template directory name to Neovim filetype.
LANGUAGE_MAP = {
    "c": "c",
    "cl": "lisp",
    "sh": "sh",
    "html": "html",
    "make": "make",
    "awk": "awk",
    "vim": "vim",
    "sed": "sed",
}

# Map from root-level template file name to Neovim filetype.
ROOT_FILE_MAP = {
    "openrc.init": "sh",
    "git-config-branch": "gitconfig",
    "uad.json": "json",
}

# <++> is an unnamed placeholder. <+name+> is a named placeholder.
PLACEHOLDER_RE = re.compile(r"<\+([^+>]*)\+>")

# A summary comment on the first line of a template, in any supported comment syntax.
HEAD_COMMENT_RE = re.compile(r"^\s*(?:#+|;+|//|<!--)\s+(.*?)\s*(?:-->)?\s*$")


def escape_snippet_text(text: str) -> str:
    """Escape the characters that VSCode snippet syntax treats as special."""
    return re.sub(r"([\\$}])", r"\\\1", text)


def convert_placeholders(content: str) -> Tuple[str, int]:
    """Replace each placeholder with a numbered tab stop. Escape all other text.

    <++> becomes ${n}. <+name+> becomes ${n:name}.
    """
    parts = PLACEHOLDER_RE.split(content)
    body = escape_snippet_text(parts[0])
    count = 0
    for name, text in zip(parts[1::2], parts[2::2]):
        count += 1
        stop = f"${{{count}:{escape_snippet_text(name)}}}" if name else f"${{{count}}}"
        body += stop + escape_snippet_text(text)
    return body, count


def generate_snippet_name(filepath: Path, template_dir: Path) -> str:
    """Join the path parts with dashes: sh/trap/cleanup-temp -> sh-trap-cleanup-temp."""
    rel_path = filepath.relative_to(template_dir).with_suffix("")
    return "-".join(rel_path.parts)


def get_description(filepath: Path, template_dir: Path) -> str:
    """Use the summary comment on the first line. Fall back to the path."""
    lines = filepath.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].startswith("#!"):
        lines = lines[1:]
    match = HEAD_COMMENT_RE.match(lines[0]) if lines else None
    if match and match.group(1):
        return match.group(1)
    rel_path = filepath.relative_to(template_dir)
    return f"{rel_path} template"


def process_template_file(filepath: Path, template_dir: Path) -> Optional[Dict[str, Any]]:
    """Read one template file. Return None when it is not a template."""
    try:
        content = filepath.read_text(encoding="utf-8").strip()
    except (UnicodeDecodeError, PermissionError):
        return None

    if not content or not PLACEHOLDER_RE.search(content):
        return None

    body, _ = convert_placeholders(content)
    return {
        "prefix": generate_snippet_name(filepath, template_dir),
        "body": body.split("\n") + ["$0"],
        "description": get_description(filepath, template_dir),
    }


def language_for(filepath: Path, template_dir: Path) -> Optional[str]:
    """Return the Neovim filetype for a template path, or None when unknown."""
    rel_path = filepath.relative_to(template_dir)
    if len(rel_path.parts) > 1:
        return LANGUAGE_MAP.get(rel_path.parts[0])
    return ROOT_FILE_MAP.get(rel_path.name)


def collect_templates_by_language(template_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Collect all templates under template_dir, grouped by filetype."""
    templates_by_lang: Dict[str, List[Dict[str, Any]]] = {}

    for filepath in sorted(template_dir.rglob("*")):
        if not filepath.is_file():
            continue
        rel_path = filepath.relative_to(template_dir)
        if any(part.startswith(".") for part in rel_path.parts):
            continue

        lang = language_for(filepath, template_dir)
        if lang is None:
            continue

        snippet = process_template_file(filepath, template_dir)
        if snippet is not None:
            templates_by_lang.setdefault(lang, []).append(snippet)

    return templates_by_lang


def write_snippet_files(templates_by_lang: Dict[str, List[Dict[str, Any]]], output_dir: Path) -> None:
    """Write one <lang>.json per language and a package.json that lists them."""
    output_dir.mkdir(parents=True, exist_ok=True)
    contributed = []

    for lang, snippets in sorted(templates_by_lang.items()):
        snippet_obj = {snippet["prefix"]: snippet for snippet in snippets}
        output_file = output_dir / f"{lang}.json"
        output_file.write_text(
            json.dumps(snippet_obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        contributed.append({"language": lang, "path": f"./{lang}.json"})
        print(f"Created {output_file} with {len(snippet_obj)} snippets")

    package = {
        "name": "tmpl-snippets",
        "contributes": {"snippets": contributed},
    }
    (output_dir / "package.json").write_text(
        json.dumps(package, indent=2) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "template_dir",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="directory that holds the templates (default: this script's directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.home() / ".config/nvim/snippets",
        help="directory to write snippet files into (default: ~/.config/nvim/snippets)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list the snippets that would be written, write nothing",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    templates_by_lang = collect_templates_by_language(args.template_dir)

    if not templates_by_lang:
        print("No templates with <++> placeholders found.")
        return

    if args.dry_run:
        for lang, snippets in sorted(templates_by_lang.items()):
            for snippet in snippets:
                print(f"{lang}\t{snippet['prefix']}")
        return

    write_snippet_files(templates_by_lang, args.output)
    print("\nDone. Load the snippets in Neovim with:")
    print(f'  require("luasnip.loaders.from_vscode").lazy_load({{ paths = {{ "{args.output}" }} }})')


if __name__ == "__main__":
    main()
