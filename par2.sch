;(multiple activations before argument evaluation completes)
(:= k (fn (a) a))
(par
	(print (* ((vau () % (seq (<- k return) 2))) (+ (+ (+ 1 1) 1) 1)))
	(k 5)
	(k 6)
	(k 7)
	0)
;(An argument that never returns)
(print ((vau () % (seq (<- k return) 1))))
(:= k2 nil)
(par
	(print	(list ((vau () % (seq (<- k2 return) (k 3)))) 3))
	((vau () % (if (nil? k2) (self) (k2 1)))))

		
