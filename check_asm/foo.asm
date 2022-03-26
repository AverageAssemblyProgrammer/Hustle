global _start
section .text
_start:
    section .data
message: db    `Hello, World\n`         ; hardcoded newlines as newlines not supported yet
section .text
    mov rax, 1                        ; syscall for write
    mov rdi, 1                        ; file handle 1 is stdout
    mov rsi, message                       ; ardress of the string to output
    mov rdx, 14                      ; numbers of bytes for the memory of the variable value
    syscall                           ; invoke the operating system to do a write
section .text
    mov    rax, 60                  ; system call for exit
    mov    rdi, 0                   ; exit code 0
    syscall
