(:= mul (fn (a b) (* a b)))
(seq
	(print (mul (+ 1 2) 3))
	(print (* 4 5))
	(print (+ 10 12))
	(print 7))
(par
	(print (mul (+ 1 2) 3))
	(print (* 4 5))
	(print (+ 10 12))
	(print 7))
