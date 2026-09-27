"""Tests for convert_to_luasnip."""

import json
import re
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

import convert_to_luasnip as conv

PLACEHOLDER = "<++>"


def unescape(text: str) -> str:
    """Reverse VSCode snippet escaping. Reference for the round trip."""
    return re.sub(r"\\([\\$}])", r"\1", text)


text_without_placeholder = st.text().filter(lambda s: "<+" not in s)


@given(text_without_placeholder)
def test_escape_round_trip(text):
    body, count = conv.convert_placeholders(text)
    assert count == 0
    assert unescape(body) == text


@given(st.lists(text_without_placeholder, min_size=1, max_size=6))
def test_placeholder_count_matches_tab_stops(chunks):
    source = PLACEHOLDER.join(chunks)
    body, count = conv.convert_placeholders(source)
    assert count == len(chunks) - 1
    stops = re.findall(r"(?<!\\)\$\{(\d+)\}", body)
    assert stops == [str(i) for i in range(1, count + 1)]
    assert unescape(re.sub(r"(?<!\\)\$\{\d+\}", PLACEHOLDER, body)) == source


def test_shell_variable_is_escaped():
    body, _ = conv.convert_placeholders('for i do echo "$i"; done')
    assert body == 'for i do echo "\\$i"; done'


def test_make_variable_is_escaped():
    body, _ = conv.convert_placeholders("$(FOLDER) : | <++>")
    assert body == "\\$(FOLDER) : | ${1}"


def test_backslash_and_brace_are_escaped():
    body, _ = conv.convert_placeholders("printf %s\\\\n; { x; }")
    assert body == "printf %s\\\\\\\\n; { x; \\}"


def test_snippet_body_ends_with_final_tab_stop(tmp_path):
    root = tmp_path / "tmpl"
    (root / "sh").mkdir(parents=True)
    (root / "sh" / "thing").write_text("echo <++>\n")
    snippet = conv.process_template_file(root / "sh" / "thing", root)
    assert snippet["body"] == ["echo ${1}", "$0"]


def test_prefix_joins_path_parts(tmp_path):
    root = tmp_path / "tmpl"
    (root / "sh" / "trap").mkdir(parents=True)
    f = root / "sh" / "trap" / "cleanup-temp"
    f.write_text("<++>")
    assert conv.generate_snippet_name(f, root) == "sh-trap-cleanup-temp"
    (root / "c").mkdir()
    g = root / "c" / "main.c"
    g.write_text("<++>")
    assert conv.generate_snippet_name(g, root) == "c-main"


def test_common_lisp_maps_to_lisp_filetype():
    assert conv.LANGUAGE_MAP["cl"] == "lisp"
    assert conv.LANGUAGE_MAP["sh"] == "sh"


def test_files_without_placeholder_are_skipped(tmp_path):
    root = tmp_path / "tmpl"
    (root / "sh").mkdir(parents=True)
    (root / "sh" / "note").write_text("just prose\n")
    assert conv.process_template_file(root / "sh" / "note", root) is None


def test_write_creates_package_json(tmp_path):
    out = tmp_path / "snippets"
    conv.write_snippet_files({"sh": [{"prefix": "sh-x", "body": ["$1"], "description": "x"}]}, out)
    package = json.loads((out / "package.json").read_text())
    assert package["contributes"]["snippets"] == [{"language": "sh", "path": "./sh.json"}]
    assert json.loads((out / "sh.json").read_text())["sh-x"]["prefix"] == "sh-x"


def test_named_placeholder_becomes_named_tab_stop():
    body, count = conv.convert_placeholders("[remote \"<+name+>\"] <++>")
    assert body == '[remote "${1:name}"] ${2}'
    assert count == 2


@given(st.text(alphabet=st.characters(blacklist_characters="+>"), min_size=1, max_size=8))
def test_named_placeholder_name_is_escaped(name):
    body, _ = conv.convert_placeholders(f"<+{name}+>")
    assert body == "${1:" + conv.escape_snippet_text(name) + "}"


def test_description_comes_from_head_comment(tmp_path):
    root = tmp_path / "tmpl"
    (root / "sh").mkdir(parents=True)
    f = root / "sh" / "thing"
    f.write_text("#!/bin/sh\n# Print the thing\necho <++>\n")
    assert conv.get_description(f, root) == "Print the thing"
    g = root / "sh" / "lisp"
    g.write_text(";; Lisp style\n(<++>)\n")
    assert conv.get_description(g, root) == "Lisp style"
    h = root / "sh" / "page"
    h.write_text("<!-- Html style -->\n<++>\n")
    assert conv.get_description(h, root) == "Html style"


def test_description_falls_back_to_path(tmp_path):
    root = tmp_path / "tmpl"
    (root / "sh").mkdir(parents=True)
    f = root / "sh" / "bare"
    f.write_text("echo <++>\n")
    assert conv.get_description(f, root) == "sh/bare template"
