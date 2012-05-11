### built-in globals

from stypes import Env, Tail, ArgK, Closure, SClos, SSym, SNum, SBool, SList, SEnv
from seval import eval, SPromise
from sparser import parse, to_string

def defvar(k,v,sym,e):
	if sym.tag != 'sym':
		raise SyntaxError("Variable Names Must Be Symbols")
	var = sym.value
	def def_k(val):
		v[var] = val
		return k(val)
	return Tail(e,v,def_k)
	
def setvar(k,v,sym,e):
	if sym.tag != 'sym':
		raise SyntaxError("Variable Names Must Be Symbols")
	var = sym.value
	def set_k(val):
		v.find(var)[var] = val
		return k(val)
	return Tail(e,v,set_k)

def cond(k,v,*x):
	if len(x) == 0:
		raise ValueError("No Branch Evaluates to True")
	else:
		(p, e) = x[0]
		return Tail(p,v,lambda vp: Tail(e,v,k) if vp.strict().value else cond(k,v,*x[1:]))

def sequence(k,v,*x):
	if len(x) == 0: return k(None)
	return Tail(x[0],v,k if len(x) == 1 else lambda vx: sequence(k,v,*x[1:]))

def cps_map_eval(callback,v,*x):
	arglen = len(x)
	if arglen == 0: return callback([])
	argv = [None]*arglen
	def map_loop(i):
		if i == arglen:
			return callback(argv)
		else:
			def assign_val(vmx):
				argv[i] = vmx
				return map_loop(i+1)
			def reassign(vmx):
				new_argv = argv[:]	#copy the other argument values
				new_argv[i] = vmx	#and just overwrite this one
				return callback(new_argv)
			return Tail(x[i],v,ArgK(assign_val,reassign))
	return map_loop(0)

def ewrap(k,v,p):
	def proc_k(proc):
		vp = proc.strict().value
		if hasattr(vp,'__call__'):
			return k(SClos(lambda ck,cv,*x:
				cps_map_eval(lambda vx:
					vp(ck,cv,*vx),cv,*x)))
		raise ValueError("Cannot wrap non-procedure.")
	return Tail(p,v,proc_k)

def cps_map_promise(callback,v,*x):
	def p_k(i,val):
		new_argv = argv[:]
		new_argv[i] = val
		return callback(new_argv)
	argv = [ax if ax.quote
		else SPromise(ax,v,lambda val:p_k(i,val))
		for i,ax in enumerate(x)]
	return callback(argv)

def lwrap(k,v,p):
	def proc_k(proc):
		vp = proc.strict().value
		if hasattr(vp,'__call__'):
			return k(SClos(lambda ck,cv,*x:
				cps_map_promise(lambda vx:
					vp(ck,cv,*vx),cv,*x)))
		raise ValueError("Cannot wrap non-procedure.")
	return Tail(p,v,proc_k)

def vprint(k,v,x):
	def print_k(val):
		print to_string(val)
		return k(val.strict())
	return Tail(x,v,print_k)

def make_cps_binop(op):
	return SClos(lambda k,v,x,y:
		cps_map_eval(lambda args:
			k(op(*(a.strict() for a in args))),v,x,y))

def vadd(x,y):
	return SNum(x.value+y.value)
def vsub(x,y):
	return SNum(x.value-y.value)
def vmul(x,y):
	return SNum(x.value*y.value)
def vdiv(x,y):
	vy = y.value
	if vy == 0:
		raise ArithmeticError("Divide By Zero")
	return SNum(x.value/vy)
def vgt(x,y):
	return SBool(x.value>y.value)
def vlt(x,y):
	return SBool(x.value<y.value)
def vge(x,y):
	return SBool(x.value>=y.value)
def vle(x,y):
	return SBool(x.value<=y.value)
def veq(x,y):
	return SBool(x.value==y.value)
def iseq(x,y):
	return SBool((x.tag != 'list') and (x.value == vy.value))
def cons(x,y):
	return SList([x]+y.value if y.tag == 'list' else y)
def vappend(x,y):
	if x.tag != 'list':
		raise ValueError("Cannot append to non-list.")
	return SList(x.value+y.value if y.tag == 'list' else y)

basic_env = Env({
	'+':		make_cps_binop(vadd),
	'-':		make_cps_binop(vsub),
	'*':		make_cps_binop(vmul),
	'/':		make_cps_binop(vdiv),
	'>':		make_cps_binop(vgt),
	'<':		make_cps_binop(vlt),
	'>=':		make_cps_binop(vge),
	'<=':		make_cps_binop(vle),
	'=':		make_cps_binop(veq),
	'eq?':		make_cps_binop(iseq),
	'cons':		make_cps_binop(cons),
	'append':	make_cps_binop(vappend),
	'car':		SClos(lambda k,v,x:Tail(x,v, lambda vx: k(vx.strict().value[0]))),
	'cdr':		SClos(lambda k,v,x:Tail(x,v, lambda vx: k(SList(vx.strict().value[1:])))),
	'list':		SClos(lambda k,v,*x:cps_map_eval(lambda args: k(SList(args)),v,*x)),
	'len':		SClos(lambda k,v,x:Tail(x,v,lambda vx: k(SNum(len(vx.strict().value))))),
	'symbol?':	SClos(lambda k,v,x:Tail(x,v,lambda vx: k(SBool(vx.strict().tag == 'sym')))),
	'list?':	SClos(lambda k,v,x:Tail(x,v,lambda vx: k(SBool(vx.strict().tag == 'list')))),
	'atom?':	SClos(lambda k,v,x:Tail(x,v,lambda vx: k(SBool(vx.strict().tag != 'list')))),
	'exit':		SClos(lambda k,v:exit()),
	'if':		SClos(lambda k,v,z,t,f: Tail(z,v,lambda vz: Tail((t if vz.strict().value else f),v,k))),
	'cond':		SClos(cond),
	':=':		SClos(defvar),
	'<-':		SClos(setvar),
	'vau':		SClos(lambda k,v,args,sym,body: k(SClos(Closure(v,args,sym,body)))),
	'quote':	SClos(lambda k,v,x: k(x)),
	'seq':		SClos(sequence),
	'print':	SClos(vprint),
	'eval':		SClos(lambda k,v,e,x:
				cps_map_eval(lambda args:
					Tail(args[0],args[1].strict().value,k),v,x,e)),
	'ewrap':	SClos(ewrap),
	'lwrap':	SClos(lwrap),
	'defer':	SClos(lambda k,v,x:x if x.quote else SPromise(x,v,k))
})

global_env = Env({},basic_env)
global_env.update({'$': SEnv(global_env)})
