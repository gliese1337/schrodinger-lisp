((vau (a) %
	(seq
		(:= va (eval % a))
		(print va)
		(self (+ va 1))))
	0)
