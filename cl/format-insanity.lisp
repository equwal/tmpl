;;;
;;; ~<~> manages spacing and can have multiple args and a default case
;;; ~:< right justify
;;; ~:@< centerj
;;; ~@< left
;;; ~[ (conditional) evaluates if the arg is non-zero
;;; ~[ (conditional) evaluates if the arg is non-zero
;;; ~{~} iteratek
;;; print toplevel functions
(format t "~:{~@{~A~}~}" '((a) (3 4)))

;;; print a newline unless the arg already has one

;;; print a table

(let ((row '(1 skip-me green ribbit)))
  (format nil "~& ~{~6D ~* ~8@A ~8@A~}" row))

;;; How to make a long docstring well
(defun docstringer ()
  #.(format nil "~@{~A~}"
            "This is a really long docstring. You might thing it is ugly "
            "to have a multiline docstring with spaces in it, since it "
            "makes the indentation all wrong. Instead, you can use a "
            "reader macro like this one."))

;;; something I did in stumpwm once
;; wraps at column 40
(let ((words "very long doc lkjf;ldsahfhdsfkjdsahf kjdsahfs hfldsak hflsa hsa hfas flkjdsaahf lkjsa hflas hfa"))
  (format stream (concatenate 'string "~{~<~%~1,40:;~A~> ~}")
          (split-string words " ")))

  (format t "~S~%" "\"Reader friendly: with escapes\"")
  ;; Arg is right-padding if needed.
  (format t "~30A|~%" "\"Aesthetic: without escapes\"")
  (format t "~C,~C,~:C~%" #\F #\Space #\Space);character, or ':' spell out
                                        ;nonprinting
  (format t "asdf~&");"fresh line" good for repeated formats
  ;; "Readable" numbers
  (format t "~R~%" 4);four
  (format t "~:R~%" 4);fourth
  (format t "~@R~%" 4);IV
  (format t "~:@R~%" 4);IIII
  (format t "~2R" 4);100
  ;; dec, bin, oct, hex
  (format t "~d~%" 4)
  (format t "~b~%" 4)
  (format t "~o~%" 8)
  (format t "~x~%" 17)
  ;; Floats
  ;; form ~width,digits after decimal, move decimal n, overflow char, padcharN
  ;; @ show + sign too
  ;; ~: group with commas. ~:comma-char, comma-group-len
  (format t "~F~%" pi)
  (format t "~E~%" pi)
  (format t "~G~%" pi)
  (format t "~$~%" pi)
  ;; v inside of args takes one
  (format t "~,,v,3:D~%" #\. 100000);Brazilian integers
  ;; # inside of args denotes cardinality
  (format t "~#~~%" 1 2 3 4); ~~~~
  (let ((*print-length* 1))
    (format t "~W~%" '(1 2)));obey printing control variables
  (format t "~:W~%" '(1 2 #\Space)) ;also use *print-pretty* as T
  ;; Infamous plurality operator:
  ;; note: how do you give back arguments?
  (format t "~R squiggl~@P~%" 1 1)
  (format t "~R squiggl~@P~%" 2 2)
  (format t "~R banana~P~%" 1 1)
  (format t "~R banana~P~%" 2 2)
  ;; Custom functions (custom plurality)
  ;; (format t "sn: squiggl~/e-ies/ pl: squiggl~/e-ies/" 1 2)
  ;; Change case
  (format t "~(~S~)~%" "DON'T YELL")
  (format t "~:(~S~)~%" "harry potter and the sorcerer's stone.");careful!
  (format t "~:@(I'm winning~)~%--~:(charlie sheen~)~%");
  ;; "Conditional" nth with default case
  (format t "~[none~;whole~;half~;third~:;diced~]~%" 3)
  ;; testing an argument (not free inside)
  (format t "~:[insignificant~;significant~]~%"
          (let ((p-val 0.1))
            (when (< p-val 0.05) p-val)))
  ;; Using the argument only if true
  (format t "~@[significant: p=~f~]~%" 0.01)
  ;; Recursive calls on args
  (format t "~{~d~}~%" '(1 2 3));each individually
  (format t "~?" "~,,v:d,~d~%" '(#\. 1023 43));Brazilian number printer.)

  ;; always prints a newline, but Only One
  ;; uses the ~@[ which runs the condition if the value is non-nil
  ;; rather than ~[ with runs except on 0
  ;; quite a strange default choice there
(defun always-newline (arg)
    (format t "~A~@[~%~]" arg (char/= #\Newline (char arg (1- (length arg))))))

(always-newline "arg")
(always-newline (format nil "arg~%"))

;; how to only print a newline after all the arguments:
(format t "~{~a~^~%~}" '(a b c))
;; or with a space
(format t "~{~a~^ ~}" '(a b c))
