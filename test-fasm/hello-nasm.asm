	BITS 64
	%define SYS_exit 60
	%define SYS_write 1
	%define STDOUT 1
	global _start
	section .text	
_start:
	mov rax, SYS_write
	mov rdi, STDOUT
	mov rsi, hello
	mov rdx, 13
	syscall 

	mov rax, SYS_write
	mov rdi, STDOUT
	mov rsi, hello2
	mov rdx, 17
	syscall
		
	section .data
hello:	db "Hello, World", 10

hello2:	db "Hello, New, World", 10

	section .text
	mov rax, SYS_exit
	mov rdi, 0
	syscall
