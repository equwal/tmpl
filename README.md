Templates for all kinds of things. Just read a file into your editor at the cursor and jump to the `<++>` locations.

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

# Using with Vim

```vim
:read /path/to/tmpl/thing
```


Make sure to add a templating shortcut to your leader key to jump to
the `<++>` spots.
```vim
    -- Templating shortcut
    map("n", "<leader><Space>", "/<++><CR>dt>a<BS>", { desc = "Jump to next template placeholder" })
```
