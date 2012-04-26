(:= q (vau (e) % e))
(:= nil '())
(:= nil? (vau (e) % (= %::e '())))

(:= @ (vau (proc args) % %::(cons %::proc %::args)))

(:= map (vau (f l) % 
	(seq
		(:= fv %::f)
		(:= lv %::l)
		(if (nil? lv) '()
			(cons (fv (car lv)) (self fv (cdr lv)))))))

(:= fn (vau (args body) %
	(wrap %::(list vau args '$ body))))
