### built-in globals

from stypes import Env, Tail
from sparser import parse, to_string, isa, Symbol
import operator

class Closure():
	def __init__(self, clos_env, vars, sym, body):
		self.clos_env = clos_env
		self.vars = vars
		self.sym = sym
		self.body = body

	def __call__(self, k, call_env, *args):
		new_env = Env(zip(self.vars, args), self.clos_env)
		new_env[self.sym] = call_env
		if not 'self' in args: new_env['self'] = self #safe recursion
		return Tail(self.body, new_env, k)
		
	def __repr__(self):
		return "vau (%s)"%(','.join(self.vars),)

def defvar(k,v,var,e):
	def def_k(val):
		v[var] = val
		return k(val)
	return Tail(e,v,def_k)
	
def setvar(k,v,var,e):
	def set_k(val):
		v.find(var)[var] = val
		return k(val)
	return Tail(e,v,set_k)

def cond(k,v,*x):
	if len(x) == 0:
		raise ValueError("No Branch Evaluates to True")
	else:
		(p, e) = x[0]
		return Tail(p,v,lambda vp: Tail(e,v,k) if vp else cond(k,v,*x[1:]))

def sequence(k,v,*x):
	if len(x) == 0: return k(None)
	return Tail(x[0],v,k if len(x) == 1 else lambda vx: sequence(k,v,*x[1:]))
	
def vprint(k,v,x):
	def print_k(val):
		print to_string(val)
		return k(val)
	return Tail(x,v,print_k)

def cps_map_eval(k,v,*x):
	vx = []
	def map_loop(mk,mv,*mx):
		if len(mx) == 0: return k(vx)
		else:
			def assign_val(vmx):
				vx.append(vmx)
				return map_loop(mk,mv,*mx[1:])
			return Tail(mx[0],v,assign_val)
	return map_loop(k,v,*x)

def wrap(k,v,p):
	return Tail(p,v,
		lambda vp:
			k(lambda ck,cv,*x:
				cps_map_eval(lambda vx: vp(ck,cv,*vx),cv,*x)))

def make_cps_binop(op):
	return lambda k,v,x,y:Tail(x,v,lambda vx: Tail(y,v, lambda vy: k(op(vx,vy))))

basic_env = Env({
	'+':	make_cps_binop(operator.add),
	'-':	make_cps_binop(operator.sub),
	'*':	make_cps_binop(operator.mul),
	'/':	make_cps_binop(operator.div),
	'>':	make_cps_binop(operator.gt),
	'<':	make_cps_binop(operator.lt),
	'>=':	make_cps_binop(operator.ge),
	'<=':	make_cps_binop(operator.le),
	'=':	make_cps_binop(operator.eq),
	'eq?':	make_cps_binop(lambda vx,vy: (not isa(vx, list)) and (vx == vy)),
	'cons':	make_cps_binop(lambda vx,vy: [vx]+vy),
	'car':	lambda k,v,x:Tail(x,v, lambda vx: k(vx[0])),
	'cdr':	lambda k,v,x:Tail(x,v, lambda vx: k(vx[1:])),
	'list': cps_map_eval,
	'append':	make_cps_binop(operator.add),
	'len':	lambda k,v,x:Tail(x,v,lambda vx: k(len(vx))),
	'symbol?':	lambda k,v,x:Tail(x,v,lambda vx: k(isa(vx,Symbol))),
	'list?':	lambda k,v,x:Tail(x,v,lambda vx: k(isa(vx,list))),
	'atom?':	lambda k,v,x:Tail(x,v,lambda vx: k(not isa(vx,list))),
	'exit':		lambda k,v:exit(),
	'#t':	True,
	'#f':	False,
	'if':		lambda k,v,z,t,f: Tail(z,v,lambda vz: Tail((t if vz else f),v,k)),
	'cond':	cond,
	':=':	defvar,
	'<-':	setvar,
	'vau':	lambda k,v,args,sym,body: k(Closure(v,args,sym,body)),
	'quote': lambda k,v,x: k(x),
	'seq': sequence,
	'print': vprint,
	'eval': lambda k,v,e,x: Tail(x,v,lambda vx: Tail(e,v,lambda ve: Tail(vx,ve,k))),
	'wrap': wrap
})

global_env = Env({},basic_env)
global_env.update({'$': global_env})
