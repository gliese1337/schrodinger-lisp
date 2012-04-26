(:= square (vau (x) % (seq (:= xv %::x) (* xv xv))))
(print (map square '(1 2 3 4)))

(:= lsqr (fn (x) (* x x)))
(print (map lsqr '(1 2 3 4)))

(print (@ lsqr '(5)))

;(fun with currying)
(:= curry (vau (f a) % 
	(seq
		(:= fv %::f)
		(:= av %::a)
		(vau (b) & (fv av &::b)))))

(:= sqrmap (curry map square))

(print (sqrmap '(1 2 3 4)))


