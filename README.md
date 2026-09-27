![template jump <++> on a transparent background](https://therealtruex.com/static/tmpl.webp)

Templates for all kinds of things. Read a file into your editor at the cursor
and jump to the `<++>` locations.

A [therealtruex.com](https://therealtruex.com) project.

Here is one such template:
```
(defpackage :<++>-system (:use :cl :asdf))
(in-package :<++>-system)
(defsystem <++>
  :name "<++>"
  :author "<++> <<++>@<++>.<++>>"
  :version "<++>"
  :maintainer "<++> <<++>@<++>.<++>>"
  :license "GNU GPLv3.0"
  :description "<++>"
  ;; put the most general files first to minimize the "depends on" use
  ;; and in that case you'll need :serial t
  :serial <++>
  :components ((:file "packages")
               (:file "<++>" :depends-on ("<++>")))
  :weakly-depends-on (<++>)
  :depends-on (<++>))
```

# Layout

One directory per language: `c`, `cl` (Common Lisp), `sh` (POSIX shell),
`sed`, `awk`, `make`, `vim`, `html`. A few loose templates sit at the root
(`openrc.init`, `git-config-branch`, `uad.json`).

Two kinds of file live here:

- **Templates** contain `<++>`. Read them in and fill the gaps.
- **Cheat sheets** contain no `<++>` (for example `sed/TLDR`, `vim/use-g-v`,
  most of `sh/`). They are notes to read or `:read` in whole. The snippet
  converter skips them.

# Using with Vim

```vim
:read /path/to/tmpl/thing
```

Add a shortcut on your leader key that jumps to the next `<++>`, deletes it,
and leaves you in insert mode.

Vimscript:
```vim
map <leader><Space> /<++><CR>dt>a<BS>
```

Lua:
```lua
map("n", "<leader><Space>", "/<++><CR>dt>a<BS>", { desc = "Jump to next template placeholder" })
```

# Using with Neovim and LuaSnip

`convert_to_luasnip.py` turns every template into a VSCode-format snippet.
Each language becomes one JSON file, and a `package.json` lists them for the
LuaSnip loader.

```sh
python3 convert_to_luasnip.py --dry-run          # list what would be written
python3 convert_to_luasnip.py                    # write to ~/.config/nvim/snippets
python3 convert_to_luasnip.py --output some/dir  # write elsewhere
```

Load the output in your Neovim config:
```lua
require("luasnip.loaders.from_vscode").lazy_load({
    paths = { vim.fn.stdpath("config") .. "/snippets" }
})
```

The snippet prefix is the path with dashes: `c/main.c` is `c-main`,
`sh/trap/cleanup-temp` is `sh-trap-cleanup-temp`. Type the prefix, press Tab,
and Tab again to move between the placeholders.

Tests:
```sh
python3 -m pip install pytest hypothesis
python3 -m pytest
```

# POSIX shell tricks

Many of the shell tricks come from https://www.etalabs.net/sh_tricks.html,
especially `sh/for-find`, a nightmare fixed-point solution.
