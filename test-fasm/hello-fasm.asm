	format ELF64 executable 3
	macro SYS_exit {60}
	macro SYS_write {1}
	macro STDOUT {1}
	segment readable executable
	entry start
start:
	mov rax, 1
	mov rdi, 1
	mov rsi, hello
	mov rdx, 13
	syscall 

	mov rax, 1
	mov rdi, 1
	mov rsi, hello2
	mov rdx, 17
	syscall
	
	mov rax, 60
	mov rdi, 0
	syscall

	segment readable writable
hello:	db "Hello, World", 10

hello2:	db "Hello, New, World", 10
