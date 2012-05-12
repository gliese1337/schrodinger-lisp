#### stypes.py

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
			self.k = rest
			return first(val)
		self.k = k

	def __call__(self,val):
		return self.k(val)
