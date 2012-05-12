;(multiple activations before argument evaluation completes)
(:= k (fn (a) a))
(par
	(print (* ((vau () % (seq (<- k return) 2))) (+ (+ (+ 1 1) 1) 1)))
	(k 5)
	(k 6)
	(k 7)
	0)

;(An argument that never returns, but is saved by another thread)
((vau () % (<- k return))) ;(grab a continuation into nothing)
(:= k2 nil)
(par
	(print	(list ((vau () % (seq (<- k2 return) (k 0)))) 3))
	((vau () % (if (nil? k2) (self) (k2 1)))))

;(An argument that never returns at all)
(print ((vau () % (+ (return 17) 2))))
