#### seval.py

from stypes import Tail, SType
from sparser import to_string

#### eval

def eval(x, env, k=lambda x:x):
	"Evaluate an expression in an environment."
	val = None
	while True:
		if not isinstance(x, SType):
			raise ValueError("Not a Shrodinger Data Type: %s"%x)
		if x.quote:
			val = k(x)
		else:
			if x.tag == 'sym':		# variable reference
				val = k(env[x.value])
			elif x.tag == 'list':		# (proc exp*)
				xv = x.value
				def capture_args():
					cx, cv, ck = xv[1:], env, k
					def try_call(proc):
						vp = proc.value
						if hasattr(vp, '__call__'):
							return vp(ck,cv,*cx)
						raise ValueError("%s = %s is not a procedure" % (to_string(xv[0]),to_string(proc)))
					return try_call
				x, k = xv[0], capture_args()
				continue
			else:
				raise ValueError("Cannot evaluate type %s"%x.tag)
	 	if not isinstance(val, Tail):
			return val
		(x,env,k) = val
