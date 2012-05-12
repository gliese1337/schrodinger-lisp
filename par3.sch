(:= spin (vau (a) % (seq (:= va (eval % a)) (if (= va 0) 0 (self (- va 1))))))

;(multiple activations from sub-threads)
(print (list	(spin 1000)
		((vau () %
			(list	(return 91)
				(return 93)
				(return 95)
				(return 97))))))
