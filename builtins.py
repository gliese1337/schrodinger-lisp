### built-in globals

from stypes import Env, Tail
from seval import eval
from sparser import parse, to_string, isa, Symbol
from threading import Thread
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

def par(k,v,*x):
	"""
	Evaluates arguments in parallel, returning the
	last listed value like sequence does.
	Ensures that all parallel threads terminate
	before continuing
	"""
	if len(x) == 0: return k(None)

	final = {'done':False,'value':None}
	def arg_k(val):	k(final['value']) if final['done'] else None

	threads = [Thread(target=lambda ax:eval(ax,v,arg_k),args=(ax,))
				for ax in x[:-1]]
	for t in threads: t.start()

	def par_k(val):
		if not final['done']:
			for t in threads: t.join()
			final['done'], final['value'] = True, val
		return k(val)
	return Tail(x[-1],v,par_k) #make use of the current thread

def cps_map_eval(k,v,*x):
	"""
	Evaluates the elements of an argument list,
	creating continuations that will assign values
	to the correct indices in the evaluated list.
	"""
	arglen = len(x)
	if arglen == 0: return k([])

	argv = [None]*arglen
	done = False
	
	def arg_thread(i,ax):
		def assign_val(val):
			if done:
				new_argv = argv[:]
				new_argv[i] = val
				return k(new_argv)
			else:
				argv[i] = val
		eval(ax,v,assign_val)

	threads = [Thread(target=arg_thread,args=(i,ax))
				for i, ax in enumerate(x[:-1])]

	for t in threads: t.start()
	arg_thread(arglen-1,x[-1]) #make use of the current thread
	for t in threads: t.join()
	
	done = True
	return k(argv)

def wrap(k,v,p):
	return Tail(p,v,
		lambda vp:
			k(lambda ck,cv,*x:
				cps_map_eval(lambda vx: vp(ck,cv,*vx),cv,*x)))

def vprint(k,v,x):
	def print_k(val):
		print to_string(val)
		return k(val)
	return Tail(x,v,print_k)

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
	'par': par,
	'print': vprint,
	'eval': lambda k,v,e,x: Tail(x,v,lambda vx: Tail(e,v,lambda ve: Tail(vx,ve,k))),
	'wrap': wrap
})

global_env = Env({},basic_env)
global_env.update({'$': global_env})
