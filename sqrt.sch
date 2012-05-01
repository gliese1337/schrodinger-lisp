(:= abs (vau (x) % (seq (:= xv %::x) (if (< 0 xv) xv (- 0 xv)))))
(:= square (vau (x) % (seq (:= xv %::x) (* xv xv))))
(:= average (vau (x y) % (* 0.5 (+ %::x %::y))))

(:= sqrt (vau (x) % (sqrt-iter 1.0 %::x)))

(:= sqrt-iter 
    (vau (guess x) % 
	  (seq
	    (:= gv %::guess)
		(:= xv %::x)
        (if (good-enough? gv xv) gv (sqrt-iter (improve gv xv) xv)))))

(:= good-enough? 
    (vau (guess x) % 
		(< (abs (- %::x (square %::guess))) 0.00001)))
(:= improve (vau (guess x) %
	(seq
		(:= gv %::guess)
		(average gv (/ %::x gv)))))

(print (sqrt 4))
(print (sqrt 2))
(print (sqrt 7))
(print (sqrt (+ 1 5)))
