(:= caar (fn (x) (car (car x))))
(:= cadr (fn (x) (car (cdr x))))
(:= cadar (fn (x) (cadr (car x))))
(:= caddr (fn (x) (cadr (cdr x))))
(:= caddar (fn (x) (caddr (car x))))

;(:= append (fn (x y)
		 ((null? x) y (cons (car x) (append (cdr x) y)))))
(:= null? (fn (x) (= x '())))
(:= pair (fn (x y) (cons x (cons y '() ))))

(:= pairlis 
    (fn (x y)
      ((null? x)
	  '()
	  (cons (pair (car x) (car y)) (pairlis (cdr x) (cdr y))))))

(:= assoc (fn (x y)
		((eq? (caar y) x) (cadar y) (assoc x (cdr y)))))

(:= eval 
    (fn (e a)
      (cond
	((atom? e) (assoc e a))
	((atom? (car e))
	 (cond
	   ((eq? (car e) (q car))   (car (eval (cadr e) a)))
	   ((eq? (car e) (q cdr))   (cdr (eval (cadr e) a)))
	   ((eq? (car e) (q cons))  (cons (eval (cadr e) a) (eval (caddr e) a)))
	   ((eq? (car e) (q atom?)) (atom? (eval (cadr e) a)))
	   ((eq? (car e) (q eq?))   (eq? (eval (cadr e) a) (eval (caddr e) a)))
	   ((eq? (car e) (q quote)) (cadr e))
	   ((eq? (car e) (q q))     (cadr e))
	   ((eq? (car e) (q cond))  (evcon (cdr e) a))
	   (#t                   (eval (cons (assoc (car e) a) (cdr e)) a))))
	((eq? (caar e) (q fn))
	 (eval (caddar e) (append (pairlis (cadar e) (evlis (cdr e) a)) a))))))

(:= evcon 
    (fn (c a)
      (cond ((eval (caar c) a) (eval (cadar c) a))
	    (#t              (evcon (cdr c) a)))))

(:= evlis 
    (fn (m a)
      (cond ((null? m) (q ()))
	    (#t     (cons (eval (car m) a) (evlis (cdr m) a))))))


(:= assert-equal
	(fn (x y)
		((= x y)
			(print "Passed test")
			{
				(print "Failed Test")
				(exit)
			})))

(:= assert-not-equal
	(fn (x y) ((= x y)
		{
			(print "Failed Test")
			(exit)
		}
		(print "Passed Test"))))

(assert-equal (eval 'x '((x test-value)))
	      'test-value)
(assert-equal (eval 'y '((y (1 2 3))))
	      '(1 2 3))
(assert-not-equal (eval 'z '((z ((1) 2 3))))
		  '(1 2 3))
(assert-equal (eval '(quote 7) '())
	      '7)
(assert-equal (eval '(atom? '(1 2)) '())
	      #f)
(assert-equal (eval '(eq? 1 1) '((1 1)))
	      #t)
(assert-equal (eval '(eq? 1 2) '((1 1) (2 2)))
	      #f)
(assert-equal (eval '(eq? 1 1) '((1 1)))
	      #t)
(assert-equal (eval '(car '(3 2)) '())
	      '3)
(assert-equal (eval '(cdr '(1 2 3)) '())
	      '(2 3))
(assert-not-equal (eval '(cdr '(1 (2 3) 4)) '())
		  '(2 3 4))
(assert-equal (eval '(cons 1 '(2 3)) '((1 1)(2 2)(3 3)))
	      '(1 2 3))
(assert-equal (eval '(cond ((atom? x) 'x-atomic) 
			     ((atom? y) 'y-atomic) 
			     ('#t 'nonatomic))
		    '((x 1)(y (3 4))))
	      'x-atomic)
(assert-equal (eval '(cond ((atom? x) 'x-atomic) 
			     ((atom? y) 'y-atomic) 
			     ('#t 'nonatomic))
		    '((x (1 2))(y 3)))
	      'y-atomic)
(assert-equal (eval '(cond ((atom? x) 'x-atomic) 
			     ((atom? y) 'y-atomic) 
			     ('#t 'nonatomic)) 
		    '((x (1 2))(y (3 4))))
	      'nonatomic)
(assert-equal (eval '((fn (x) (car (cdr x))) '(1 2 3 4)) '())
	      2)

(print "Passed All Tests")
(exit)
