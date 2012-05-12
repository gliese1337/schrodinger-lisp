(:= k1 nil)
(:= k2 nil)
((vau () % (<- k1 return)))

;(force blocking of sub-thread continuations)
(print (list	(+ 1 ((vau () % (seq (<- k2 return) (k1 0)))))
		(+ 1 ((vau () % (list (return 100) (return 102)))))))
(k2 0)
