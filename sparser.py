Symbol = str
isa = isinstance

def parse(tokens):
	"Read an expression from a sequence of tokens."
	try:
		token = tokens.pop(0)
		if '(' == token:
			L = []
			while tokens[0] != ')':
				subtree = parse(tokens)
				if subtree is not None: #edge case for empty comments
					L.append(subtree)
			tokens.pop(0) # pop off ')'
			return L
		elif ";" == token: #ignore the next full expression
			token = tokens[0]
			if ')' == token:
				return None
			tokens.pop(0)
			parencount  = 1 if '(' == token else 0
			while parencount > 0:
				token = tokens.pop(0)
				if '(' == token: parencount += 1
				elif ')' == token: parencount -= 1
			return parse(tokens) if len(tokens) > 0 else None
		elif ')' == token:
			raise SyntaxError('unexpected )')
		else:
			return atom(token)
	except IndexError:
		raise SyntaxError('unexpected EOF while reading')

def atom(token):
	"Numbers become numbers; every other token is a symbol."
	try: return int(token)
	except ValueError:
		try: return float(token)
		except ValueError:
			return Symbol(token) 

def to_string(exp):
	"Convert a Python object back into a Lisp-readable string."
	return '('+' '.join(map(to_string, exp))+')' if isa(exp, list) else str(exp)
