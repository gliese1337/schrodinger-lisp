(:= par (vau (a) % (car (eval % (cons list a)))))
(:= mul (fn (a b) (* a b)))
(print (par (
	(print (mul (+ 1 2) 3))
	(print (* 4 5))
	(print (+ 10 12))
	(print 7))))
