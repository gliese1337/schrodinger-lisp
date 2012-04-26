(:= square (vau (x) % (seq (:= xv (eval % x)) (* xv xv))))
(print (map square (q (1 2 3 4))))

(:= lsqr (fn (x) (* x x)))
(print (map lsqr (q (1 2 3 4))))

(print (@ lsqr (q (5))))

;(fun with currying)
(:= curry (vau (f a) % 
	(seq
		(:= fv (eval % f))
		(:= av (eval % a))
		(vau (b) & (fv av (eval & b))))))

(:= sqrmap (curry map square))

(print (sqrmap (q (1 2 3 4))))


