#!/usr/bin/env python3
import os
from os import *
from sys import *
import std.std_hustle as stdlib
from colorama import Fore

# MIT License 
# Copyright (c) 2022 Akshaj Trivedi and Hustle Contributers

if os.name == "nt":
    # you can bypass this by just deleting this if statement and then make it compatable with windows, well it is quite compatable just need to change few things
    print("this file is not windows compatable yet")

def usage(white_help=True):
	if white_help:
		print(Fore.WHITE + "Subcommands are :-") 
		print(Fore.WHITE + "    run    <filepath>    " + "         - interprete the program.")
		print(Fore.WHITE + "    com    <filepath>    " + "         - compile the program.")
		print(Fore.WHITE + "    com -r <filepath>    " + "         - run the compiled program.")
		print(Fore.WHITE + "    help                 " + "         - print this help screen.")
	else: 
		print("Subcommands are :-")
		print("    run    <filepath>    " + "         - run will interprete the program.")
		print("    com    <filepath>    " + "         - compile the program.")
		print("    com -r <filepath>	" + "         - run the compiled program.")
		print("    help                 " + "         - help will print this help screen.")


def check_subcommand(command):
	if command.lower() == "run":
		return "run"
	elif command.lower() == "help":
		ret = "help"
		return ret
	elif command.lower() == "com" or command == "compile": 
		return "com"
	else:
		print("Unkown Subcommand")
		usage()


def throw_error(error, code):
	print(Fore.RED + "ERROR: " + error)
	usage()
	exit(code)

def run():
	try:
		subcommand = argv[1]
		struct = check_subcommand(subcommand)
	except:
		# TODO: unhardcode this error 
		throw_error("No Subcomand Provided", 1)
	try:
		if struct == "run":	
			data = argv[2]
			text = "run(\""+data+"\")"
			result, error = stdlib.run('<stdin>', text)
			if error:
				print(error.as_string())
			elif result:
				if len(result.elements) == 1:
					print(repr(result.elements[0]))
				else:
					print(repr(result)) 
	except Exception as e:	
		if str(e) == "list index out of range":
			if argv[2] == data:
				return 
			else:
				throw_error("No File Provided", 1)
		else: 
			print("\n")
			print(e)
			exit(1)
	# COMPILE MODE IS STILL IN PROGRESS AND NOT COMPLETE
	if struct == "com":
		subsubcommand = argv[2]
		ispath = False 
		if subsubcommand is not None: 
			if str(subsubcommand) == "-r":
				data1 = argv[3]
				text1 = "com_run(\""+data1+"\")"
				stdlib.com_run('<stdin>', text1, data1)
				stdlib.run_compiled_code(data1, '.hsle')
			elif subsubcommand.endswith('.hsle'):
				subsubcommand = subsubcommand[:-len('.hsle')]
				ispath = True
		if ispath:
			data2 = argv[2]
			text = "com_run(\""+data2+"\")"
			stdlib.com_run('<stdin>', text, data2)
	elif struct == "help":
		usage(False)
		exit(0)

if __name__ in '__main__':
	run()
