#!/usr/bin/env python3

# THIS IS JUST FOR TESTING, I MADE THIS LIGHTWIGHT SO THERE IS NOT ERROR REPORTING AND NO HELP SUBCOMAND
import std.Interpreter as stdlib
from sys import *

def open_file(filename):
	if filename.endswith('.hsle'):
		data = filename
		return data
	else:
		data = filename
		return data 

def out_run():
    data = open_file(argv[1])
    text = "run(\""+data+"\")"
    result, error = stdlib.run('<stdin>',text)
    if error:
        print(error.as_string())
    elif result:
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))
out_run() 