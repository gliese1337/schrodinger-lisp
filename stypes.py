#### stypes.py

isa = isinstance

class SType():
	def __init__(self,tag,val,quote=True):
		self.tag = tag
		self.value = val
		self.quote = quote
	def __repr__(self):
		return "<%s: %s>"%(self.tag,self.value)
	def __str__(self):
		return self.__repr__()
	def strict(self):
		return self

def SList(l): return SType('list',l,False)
def SSym(s): return SType('sym',s,False)
def SNum(n): return SType('num',n)
def SBool(b): return SType('bool',b)


### binding environments

class Env(dict):
	"An environment: a dict of {'var':val} pairs, with an outer Env."
	def __init__(self, bindings={}, outer=None):
		self.update(bindings)
		self.outer = outer

	def __getitem__(self, var):
		return super(Env,self.find(var)).__getitem__(var)

	def find(self, var):
		"Find the innermost Env where var appears."
		if var in self:
			return self
		elif not self.outer is None:
			return self.outer.find(var)
		else: raise ValueError("%s is not defined"%(var,))

def SEnv(e): return SType('env',e)


### callables: closures and continuations

class Continuation():
	def __init__(self,k):
		self.k = k
	def __call__(self, call_k, call_env, *args):
		if len(args) != 1: raise Exception("Continuations take exactly 1 argument.")
		return Tail(args[0],call_env,self.k)

class Closure():
	def __init__(self, clos_env, vars, sym, body):
		self.clos_env = clos_env
		self.vars = []
		if vars.tag != 'list':
			raise SyntaxError("No Argument Name List")
		for asym in vars.value:
			if asym.tag == 'sym': self.vars.append(asym.value)
			else: raise SyntaxError("Argument Names Must Be Symbols")
		if sym.tag == 'sym': self.sym = sym.value
		else: raise SyntaxError("Environment Binding Name Must Be a Symbol")
		self.body = body

	def __call__(self, k, call_env, *args):
		new_env = Env(zip(self.vars, args), self.clos_env)
		new_env[self.sym] = SEnv(call_env)
		if not 'self' in args: new_env['self'] = SClos(self) #safe recursion
		if not 'return' in args: new_env['return'] = SClos(Continuation(k))
		return Tail(self.body, new_env, k)

	def __repr__(self):
		return "vau (%s)"%(','.join(self.vars),)


def SClos(c): return SType('closure',c)


### tail call structure

class Tail():
	def __init__(self,expr,env,k):
		self.expr = expr
		self.env = env
		self.k = k
	
	def __iter__(self):
		yield self.expr
		yield self.env
		yield self.k


### self-modifying continuations for argument evaluation

class ArgK():
	def __init__(self,first,rest):
		def k(val):
			r = first(val)
			self.k = rest
			return r
		self.k = k

	def __call__(self,val):
		return self.k(val)
