        .text
        .globl main

main:
        movq    $2, x
        movq    x, %rcx
        imul    %rcx, %rcx
        movq    %rcx, y
        movq    x, %rdi
        addq    y, %rdi
        call print_int
        ret


print_int:
        mov     %rdi, %rsi
        mov     $message, %rdi  # arguments pour printf
        mov     $0, %rax
        call    printf
        ret


        .data
message: 
        .string "%d\n"

x: 
        .quad 0

y: 
        .quad 0
