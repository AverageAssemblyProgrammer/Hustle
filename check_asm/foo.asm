global _start
section .text
_start:
    mov    rax, 1                 ; sys call for write
    mov    rdi, 1                 ; file handle 1 is stdout
    mov    rsi, message           ; ardress of string to output
    mov    rdx, 13    ; numbers of bytes for the memory of the string
    syscall                       ; invoke the os to do the write
    mov    rax, 60                ; system call for exit
    xor    rdi, rdi               ; exit code 0
    syscall
    section     .data
message: db     "Hello World", 10     ; note the newline at the end
