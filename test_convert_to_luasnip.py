"""Tests for convert_to_luasnip."""

import json
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

import convert_to_luasnip as conv

PLACEHOLDER = "<++>"


def parse_snippet(body: str):
    """Reference parser for VSCode snippet text.

    Return the source text with placeholders restored, and the list of tab
    stop numbers in order. This is the inverse of convert_placeholders.
    """
    out, stops, i = [], [], 0
    while i < len(body):
        c = body[i]
        if c == "\\" and i + 1 < len(body) and body[i + 1] in "\\$}":
            out.append(body[i + 1])
            i += 2
        elif body.startswith("${", i):
            i += 2
            inner = []
            while body[i] != "}":
                if body[i] == "\\" and body[i + 1] in "\\$}":
                    inner.append(body[i + 1])
                    i += 2
                else:
                    inner.append(body[i])
                    i += 1
            i += 1
            num, _, name = "".join(inner).partition(":")
            stops.append(num)
            out.append(f"<+{name}+>" if name else PLACEHOLDER)
        else:
            assert c not in "$}", f"unescaped {c!r} at {i} in {body!r}"
            out.append(c)
            i += 1
    return "".join(out), stops


text_without_placeholder = st.text().filter(lambda s: "<+" not in s)


@settings(max_examples=500)
@given(text_without_placeholder)
def test_escape_round_trip(text):
    body, count = conv.convert_placeholders(text)
    assert count == 0
    assert parse_snippet(body) == (text, [])


@settings(max_examples=500)
@given(st.lists(text_without_placeholder, min_size=1, max_size=6))
def test_placeholder_count_matches_tab_stops(chunks):
    source = PLACEHOLDER.join(chunks)
    body, count = conv.convert_placeholders(source)
    assert count == len(chunks) - 1
    assert parse_snippet(body) == (source, [str(i) for i in range(1, count + 1)])


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


@settings(max_examples=500)
@given(st.text(alphabet=st.characters(blacklist_characters="+>"), min_size=1, max_size=8))
def test_named_placeholder_round_trip(name):
    body, count = conv.convert_placeholders(f"<+{name}+>")
    assert count == 1
    assert parse_snippet(body) == (f"<+{name}+>", ["1"])


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
    g = root / "sh" / "cfile"
    g.write_text("#include <stdio.h>\n<++>\n")
    assert conv.get_description(g, root) == "sh/cfile template"


REPO = Path(__file__).resolve().parent


def test_every_repo_template_has_a_summary():
    """Every file with a placeholder starts with a summary comment. JSON has no comments."""
    missing = []
    for lang, snippets in conv.collect_templates_by_language(REPO).items():
        for snippet in snippets:
            if lang != "json" and snippet["description"].endswith(" template"):
                missing.append(snippet["prefix"])
    assert missing == []
