### built-in globals

from stypes import Env
from seval import eval
from sparser import parse, to_string, isa, Symbol

class Combiner():
	def __init__(self, clos_env, vars, sym, body):
		self.clos_env = clos_env
		self.vars = vars
		self.sym = sym
		self.body = body

	def __call__(self, call_env, *args):
		new_env = Env(zip(self.vars, args), self.clos_env)
		new_env[self.sym] = call_env
		if not 'self' in args: new_env['self'] = self #safe recursion
		return eval(self.body, new_env)
		
	def __repr__(self):
		return "vau (%s)"%(','.join(self.vars),)

def defvar(v,var,e):
	val = eval(e, v)
	v[var] = val
	return val
	
def setvar(v,var,e):
	val = eval(e, v)
	v.find(var)[var] = val
	return val

def cond(v,*x):
	for (p, e) in x:
		if eval(p, v):
			return eval(e, v)
	raise ValueError("No Branch Evaluates to True")

def sequence(v,*x):
	val = 0
	for e in x:
		val = eval(e, v)
	return val
	
def vprint(v,e):
	val = eval(e, v)
	print to_string(val)
	return val

def wrap(v,p):
	p = eval(p,v)
	return lambda v,*x: p(v,*[eval(expr,v) for expr in x])

basic_env = Env({
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
	'list':	lambda v,*x:[eval(expr, v) for expr in x],
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
	':=':	defvar,
	'<-':	setvar,
	'vau':	lambda v,args,sym,body: Combiner(v,args,sym,body),
	'quote': lambda v,x: x,
	'seq': sequence,
	'print': vprint,
	'eval': lambda v,e,x: eval(eval(x,v),eval(e,v)),
	'wrap': wrap
})

global_env = Env({},basic_env)
global_env.update({'$': global_env})
