(:= map (vau (f l) % 
	(begin
		(:= fv (eval % f))
		(:= lv (eval % l))
		(if (> (len lv) 0)
			(cons (fv (car lv)) (map fv (cdr lv)))
			(q ())))))

(:= square (vau (x) % (begin (:= xv (eval % x)) (* xv xv))))

(print (map square (q (1 2 3 4))))

(print (eval $ (cons + (q (1 2)))))

(:= curry (vau (f a) % 
	(begin
		(:= fv (eval % f))
		(:= av (eval % a))
		(vau (b) & (fv av (eval & b))))))

(:= sqrmap (curry map square))

(print (sqrmap (q (1 2 3 4))))

(:= lambda
	(vau (formals body) env
		(wrap (eval env (list vau formals (q $) body)))))

(:= lsqr (lambda (x) (* x x)))

(print (lsqr 2))
