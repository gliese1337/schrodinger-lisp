#### seval.py

from sparser import to_string, Symbol, isa

#### eval

def eval(x, env):
	"Evaluate an expression in an environment."
	if isa(x, Symbol):		  # variable reference
		return env[x]
	elif isa(x, list):		  # (proc exp*)
		proc = eval(x[0], env)
		if hasattr(proc, '__call__'):
			return proc(env,*x[1:])
		raise ValueError("%s = %s is not a procedure" % (to_string(x[0]),to_string(proc)))
	return x
