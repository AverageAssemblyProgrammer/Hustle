global _start
section .text
_start:
section .text
    mov    rax, 1                     ; sys call for write
    mov    rdi, 1                     ; file handle 1 is stdout
    mov    rsi, string455830               ; ardress of string to output
    mov    rdx, 49                    ; numbers of bytes for the memory of the string
    syscall                           ; invoke the os to do the write
    section     .data
string455830: db     "you can even do this in hustle compilation mode, ", 10         ; note the newline at the end
section .text
    mov    rax, 1                     ; sys call for write
    mov    rdi, 1                     ; file handle 1 is stdout
    mov    rsi, string863140               ; ardress of string to output
    mov    rdx, 47                    ; numbers of bytes for the memory of the string
    syscall                           ; invoke the os to do the write
    section     .data
string863140: db     "now hustle supports multiple printh statements ", 10         ; note the newline at the end
    section .data
my_number: db    "69", 10         ; hardcoded newlines as newlines not supported yet
section .text
    mov rax, 1                        ; syscall for write
    mov rdi, 1                        ; file handle 1 is stdout
    mov rsi, my_number                       ; ardress of the string to output
    mov rdx, 2                      ; numbers of bytes for the memory of the variable value
    syscall                          ; invoke the operating system to do a write
section .text
    mov    rax, 60                  ; system call for exit
    mov    rdi, 0                   ; exit code 0
    syscall
