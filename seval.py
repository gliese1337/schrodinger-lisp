#### seval.py

from stypes import Tail
from sparser import to_string, Symbol, isa

#### eval

def eval(x, env, k=lambda x:x):
	"Evaluate an expression in an environment."
	val = None
	while True:
		if isa(x, Symbol):		  # variable reference
			val = k(env[x])
		elif isa(x, list):		  # (proc exp*)
			def capture_args():
				cx, cv, ck = x[1:], env, k
				def try_call(proc):
					if hasattr(proc, '__call__'):
						return proc(ck,cv,*cx)
					raise ValueError("%s = %s is not a procedure" % (to_string(x[0]),to_string(proc)))
				return try_call
			x, k = x[0], capture_args()
			continue
		else:
			val = k(x)
		if not isa(val, Tail):
			return val
		(x,env,k) = val
