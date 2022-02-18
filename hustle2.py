#!/usr/bin/env python3

# this is just a small modified version of the other hustle code runner, but this is used for testing argv and argc in hustle

from sys import *
import std.Interpreter as stdlib
from colorama import Fore

# MIT License 
# Copyright (c) 2022 Akshaj Trivedi and Hustle Contributers

def open_file(filename):
	if filename.endswith('.hsle'):
		data = filename
		return data
	else:
		data = filename
		return data 

def usage(white_help=True):
	if white_help:
		print(Fore.WHITE + "Subcommands are :-")
		print(Fore.WHITE + "  <filepath>" + "          - will run the file that was provided")
		print(Fore.WHITE + "    help" +     "          - help will print this help screen")
	else: 
		print("Subcommands are :-")
		print("   <filepath>" + "         - will run the file that was provided")
		print("    help" + "              - help will print this help screen")

def throw_error(error, code):
	print(Fore.RED + "ERROR: " + error)
	usage()
	exit(code)

def run():	
        try:
            data = open_file(argv[1])
            if data == "help":
                usage()
                exit(0)
            text = "run(\""+data+"\")"
            result, error = stdlib.run('<stdin>',text)
            if error:
                print(error.as_string())
            elif result:
                if len(result.elements) == 1:
                    print(repr(result.elements[0]))
                else:
                    print(repr(result))
        except Exception as e:	
            if str(e) == "list index out of range":
                throw_error("No File Provided", 1)	
            else: 
                print("\n")
                print(e)
                usage()
                exit(1)

run() 
