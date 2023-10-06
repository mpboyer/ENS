        .text
        .globl main

main: 
        sub     $16, %rsp
        movq    $3, 8(%rsp) 
        mov     8(%rsp), %rdi
        imul    8(%rsp), %rdi
        call    print_int

        movq    $3, 8(%rsp)
        mov     8(%rsp), %rax
        add     %rax, %rax
        movq    %rax, (%rsp)
        imul    8(%rsp), %rax
        mov     %rax, %rdi

        mov     8(%rsp), %rax
        add     $3, %rax
        mov     %rax, (%rsp)
        
        mov     $0, %rdx
        mov     (%rsp), %rax
        idivq   %rax
        add     %rax, %rdi
        call    print_int
        
        add     $16, %rsp
        mov     $0, %rax
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


