import string

def spaceState(s,i):
	try:
		while s[i] in string.whitespace: i += 1
	except IndexError:
		return None,"",None
	return symbolState,"",i

def delimState(s,start):
	i = start+1
	return symbolState,s[start:i],i

def symbolState(s,start):
	i = start
	try:
		while True:
			if s[i] in string.whitespace:
				return spaceState,s[start:i],i
			if s[i] in "();":
				return delimState,s[start:i],i
			i += 1
	except IndexError:
		return None,s[start:i-1],None

def tokenize(s):
	state = symbolState
	pos = 0
	tokens = []
	while state != None:
		state,token,pos = state(s,pos)
		if token != "":
			tokens.append(token)
	return tokens
