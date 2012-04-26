#### vernal.py
#
# Interface for the Vernal interpreter

import os
import sys
import traceback
import readline
import atexit
from seval import eval
from sparser import tokenize, parse, to_string
from builtins import global_env

#### Load from a file and run

def load(filename):
	print "Loading and executing %s" % filename
	rps = 0
	full_line = ""
	line_num = 1
	for line in open(filename, "r"):
		line = line.strip()
		full_line += line
		rps += line.count("(")-line.count(")")
		if rps == 0 and full_line.strip() != "":
			try:
				tokens = tokenize(full_line)
				while len(tokens) > 0:
					val = eval(parse(tokens),global_env)
			except SystemExit:
				exit()
			except Exception as e:
				print "\nAn error occurred on line %d:\n\t%s\n" % (line_num,full_line)
				print e.message
				#traceback.print_exc()
				break
			full_line = ""
		line_num += 1

#### repl

def repl(prompt='vau> '):
	try:
		while True:
			full_line = raw_input(prompt)
			rps = full_line.count("(")-full_line.count(")")
			while rps != 0 or full_line == "":
				line = raw_input(">\t")
				full_line += line
				rps += line.count("(")-line.count(")")
			try:
				tokens = tokenize(full_line)
				while len(tokens) > 0:
					val = eval(parse(tokens),global_env)
					if val is not None: print to_string(val)
			except ValueError as e:
				print e.message
	except (KeyboardInterrupt, SystemExit):
		pass
	except:
		print "\nFatal Error\n"
		traceback.print_exc()
		
#### on startup from the command line

def main():
	histfile = os.path.expanduser("~/.schroedinger-history")
	try: readline.read_history_file(histfile)
	except IOError: pass

	atexit.register(readline.write_history_file, histfile)

	load("./stdlib.sch")

	if len(sys.argv) > 1:
		load(sys.argv[1])
	repl()

if __name__ == "__main__":
	main()
