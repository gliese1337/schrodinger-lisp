(:= k1 nil)
(:= k2 nil)
((vau () % (<- k1 return)))

(:= spin (fn (a) (if (= a 0) 0 (self (- a 1)))))

;(multiple activations from sub-threads)
(print (list	(spin 10000)
		((vau () %
			(list	(return 91)
				(return 93)
				(return 95)
				(return 97))))))

;(force blocking of sub-thread continuations)
(print (list	(+ 1 ((vau () % (seq (<- k2 return) (k1 0))))
		(+ 1 ((vau () % (list (return 100) (return 102)))))))
(k2 0)
