### built-in globals

from stypes import Env, Tail
from sparser import parse, to_string, isa, Symbol
import operator

class Continuation():
	def __init__(self,k):
		self.k = k
	
	def __call__(self, call_k, call_env, *args):
		if len(args) != 1: raise Exception("Continuations take exactly 1 argument.")
		return Tail(args[0],call_env,self.k)

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
		if not 'return' in args: new_env['return'] = Continuation(k)
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
	"""
	Evaluates the elements of an argument list,
	creating continuations that will assign values
	to the correct indices in the evaluated list.
	"""
	arglen = len(x)
	if arglen == 0: return k([])
	argv = [None]*arglen
	done = [False]
	def map_loop(mk,mv,i,*mx):
		if len(mx) == 0:
			done[0] = True
			return k(argv)
		else:
			def assign_val(vmx):
				if not done[0]:	#on the first time through,
					argv[i] = vmx		#evaluate the next argument in the list
					return map_loop(mk,mv,i+1,*mx[1:])
				else: #if this is a continuation call,
					new_argv = argv[:]	#copy the other argument values
					new_argv[i] = vmx	#and just overwrite this one
					return k(new_argv)
			return Tail(mx[0],v,assign_val)
	return map_loop(k,v,0,*x)

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
