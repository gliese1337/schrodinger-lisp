### built-in globals

from seval import eval, Env
from sparser import to_string, isa, Symbol

def vau(clos_env, vars, call_env_sym, body):
		def closure(call_env, *args):
			#new_env = Env(zip(vars, args), clos_env)
			new_env = Env(zip(vars, [call_env[arg] if isa(arg, Symbol) else arg for arg in args]), clos_env)
			new_env[call_env_sym] = call_env
			return eval(body, new_env)
		return closure

def define(v,var,e):
	val = eval(e, v)
	v[var] = val
	return val
	
def setvar(v,var,e):
	val = eval(e, v)
	env.find(var)[var] = val
	return val

def quote(v,exp): return exp

def cond(v,*x):
	for (p, e) in x:
		if eval(p, v):
			return eval(e, v)
	raise ValueError("No Branch Evaluates to True")

def begin(v,*x):
	val = 0
	for e in x:
		val = eval(e, v)
	return val
	
def vprint(v,e):
	val = eval(e, v)
	print to_string(val)
	return val

global_env = Env({
	'+':	lambda v,x,y:eval(x,v)+eval(y,v),
	'-':	lambda v,x,y:eval(x,v)-eval(y,v),
	'*':	lambda v,x,y:eval(x,v)*eval(y,v),
	'/':	lambda v,x,y:eval(x,v)/eval(y,v),
	'>':	lambda v,x,y:eval(x,v)>eval(y,v),
	'<':	lambda v,x,y:eval(x,v)<eval(y,v),
	'>=':	lambda v,x,y:eval(x,v)>=eval(y,v),
	'<=':	lambda v,x,y:eval(x,v)<=eval(y,v),
	'=':	lambda v,x,y:eval(x,v)==eval(y,v),
	'eq?':	lambda v,x,y:
				(lambda vx,vy: (not isa(vx, list)) and (vx == vy))(eval(x,v),eval(y,v)),
	'cons':	lambda v,x,y:[eval(x,v)]+eval(y,v),
	'car':	lambda v,x:eval(x,v)[0],
	'cdr':	lambda v,x:eval(x,v)[1:],
	'list':	lambda v,*x:[eval(expr, v) for exp in x],
	'append':	lambda v,x,y:eval(x,v)+eval(y,v),
	'len':	lambda v,x:len(eval(x,v)),
	'symbol?':	lambda v,x:isa(eval(x,v),Symbol),
	'list?':	lambda v,x:isa(eval(x,v),list),
	'atom?':	lambda v,x:not isa(eval(x,v), list),
	'exit':		lambda v:exit(),
	'#t':	True,
	'#f':	False,
	'if':		lambda v,z,t,f: eval((t if eval(z,v) else f), v),
	'cond':	cond,
	':=':	define,
	'<-':	setvar,
	'vau':	vau,
	'q': 	lambda v,x: x,
#	'quote': lambda v,x: x,
	'begin': begin,
	'print': vprint,
	'eval': lambda v,e,x: eval(eval(x,v),eval(e,v)),
	'@': lambda v,e,*x: eval(x,eval(e,v))
})
