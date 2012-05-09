(:= c nil)
(:= mul (fn (a b) (* a b)))
(print
	(mul 
		((vau () % (seq (<- c return) 2)))
		(+ 2 3)))
(c 3)
(c (+ 1 2))
(c 1 2)
