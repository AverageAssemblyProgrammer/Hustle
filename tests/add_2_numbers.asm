global _start
section .text
_start:
    section .data
number: db    "69", 10         ; hardcoded newlines as newlines not supported yet
section .text
    mov rax, 1                        ; syscall for write
    mov rdi, 1                        ; file handle 1 is stdout
    mov rsi, number                       ; ardress of the string to output
    mov rdx, 4                       ; numbers of bytes for the memory of the variable value
    syscall                       ; invoke the operating system to do a write
    mov rax, 60                       ; system call for exit
    xor rdi, rdi                        ; exit code 0
    syscall                       ; system call for exit
