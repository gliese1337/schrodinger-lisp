(:= abs (vau (x) % (seq (:= xv (eval % x)) (if (< 0 xv) xv (- 0 xv)))))
(:= square (vau (x) % (seq (:= xv (eval % x)) (* xv xv))))
(:= average (vau (x y) % (* 0.5 (+ (eval % x) (eval % y)))))

(:= sqrt (vau (x) % (sqrt-iter 1.0 (eval % x))))

(:= sqrt-iter 
    (vau (guess x) % 
	  (seq
	    (:= gv (eval % guess))
		(:= xv (eval % x))
        (if (good-enough? gv xv) gv (sqrt-iter (improve gv xv) xv)))))

(:= good-enough? 
    (vau (guess x) % 
		(< (abs (- (eval % x) (square (eval % guess)))) 0.00001)))
(:= improve (vau (guess x) %
	(seq
		(:= gv (eval % guess))
		(average gv (/ (eval % x) gv)))))

(print (sqrt 4))
(print (sqrt 2))
(print (sqrt 7))
(print (sqrt (+ 1 5)))
