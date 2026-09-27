;; Read every form in the file named on the command line. Exit 1 on a read error.
(let ((path (second sb-ext:*posix-argv*)))
  (handler-case
      (with-open-file (in path)
        (loop for form = (read in nil in)
              until (eq form in)))
    (error (e)
      (format *error-output* "~a: ~a~%" path e)
      (sb-ext:exit :code 1))))
