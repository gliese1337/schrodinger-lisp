(:= q (vau (e) % e))
(:= nil (q ()))
(:= nil? (vau (e) % (= (eval % e) (q ()))))

(:= @ (vau (proc args) % (eval % (cons (eval % proc) (eval % args)))))

(:= map (vau (f l) % 
	(seq
		(:= fv (eval % f))
		(:= lv (eval % l))
		(if (nil? lv) (q ())
			(cons (fv (car lv)) (self fv (cdr lv)))))))

(:= fn (vau (args body) %
	(wrap (eval % (list vau args (q $) body)))))
