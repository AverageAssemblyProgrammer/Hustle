#!/usr/bin/env python3
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

def check_subcommand(command):
	if command == "run" or command == "Run" or command == "RUN" or command == "-r":
		return "run"
	elif command == "Help" or command == "help" or command == "HELP" or command == "-h":
		ret = "help"
		return ret
	else:
		print("Unkown Subcommand")
		print("Subcommands are :-")
		print("    run    <filepath>" + " - run will interprete the program.")
		print("    help" + "              - help will print this help screen")
		print(Fore.RED + "exited abnormally with code 1")

def usage(white_help=True):
	if white_help:
		print(Fore.WHITE + "Subcommands are :-")
		print(Fore.WHITE + "    run    <filepath>" + " - run will interprete the program.")
		print(Fore.WHITE + "    help" + "              - help will print this help screen")
	else: 
		print("Subcommands are :-")
		print("    run    <filepath>" + " - run will interprete the program.")
		print("    help" + "              - help will print this help screen")

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
			data = open_file(argv[2])
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
			if argv[2] == data:
				return 
			else:
				throw_error("No File Provided", 1)
		else: 
			print("\n")
			print(e)
			exit(1)
	if struct == "help":
		usage()
		exit(0)

run() 
