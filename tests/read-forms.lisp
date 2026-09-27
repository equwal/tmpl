;; Read every form in the file named on the command line. Exit 1 on a read error.
;; *read-suppress* makes the reader check syntax only: it does not intern
;; symbols in packages that do not exist and does not evaluate #. forms.
(let ((path (second sb-ext:*posix-argv*))
      (*read-suppress* t))
  (handler-case
      (with-open-file (in path)
        (loop for form = (read in nil in)
              until (eq form in)))
    (error (e)
      (format *error-output* "~a: ~a~%" path e)
      (sb-ext:exit :code 1))))
