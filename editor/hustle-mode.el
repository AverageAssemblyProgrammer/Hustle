;; Thanks tsoding (Alexey Kutepov <reximkut@gmail.com>) for this file that I modified cause I am lazy
;; tsoding's language:- https://github.com/tsoding/porth

;; Copyright (C) 2021 Alexey Kutepov <reximkut@gmail.com>

;; Copyright (c) 2022 Akshaj Trivedi <akshajtrivedi189@gmail.com>

;; Permission is hereby granted, free of charge, to any person
;; obtaining a copy of this software and associated documentation
;; files (the "Software"), to deal in the Software without
;; restriction, including without limitation the rights to use, copy,
;; modify, merge, publish, distribute, sublicense, and/or sell copies
;; of the Software, and to permit persons to whom the Software is
;; furnished to do so, subject to the following conditions:

;; The above copyright notice and this permission notice shall be
;; included in all copies or substantial portions of the Software.

;; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
;; EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
;; MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
;; NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
;; BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
;; ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
;; CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
;; SOFTWARE.

(defconst hustle-mode-syntax-table
  (with-syntax-table (copy-syntax-table)
	(modify-syntax-entry ?/ ". 124b")
	(modify-syntax-entry ?* ". 23")
	(modify-syntax-entry ?\n "> b")
    (modify-syntax-entry ?' "\"")
    (syntax-table))
  "Syntax table for `hustle-mode'.")

(eval-and-compile
  (defconst hustle-keywords
    '("if" "else" "while" "then" "include" "end" "var" 
      "and" "or" "tsleep" "not" "elif" "func" "return"
      "continue" "break" "step" "sys" "int" "str"
      "float" "randint" "not" "for" "to" "printh")))

(defconst hustle-highlights
  `((,(regexp-opt hustle-keywords 'symbols) . font-lock-keyword-face)))

;;;###autoload
(define-derived-mode hustle-mode prog-mode "hustle"
  "Major Mode for editing Hustle Souce Code."
  :syntax-table hustle-mode-syntax-table
  (setq font-lock-defaults '(hustle-highlights))
  (setq-local comment-start "// "))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.hsle\\'" . hustle-mode))

(provide 'hustle-mode)
;;; porth-mode.el ends here
