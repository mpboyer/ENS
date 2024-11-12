        .text
        .globl main

main: 
        mov $1, %rdi
        test %rdi, %rdi
        jz .T0
        and $0, %rdi

.T0:
        call    print_bool
        
        mov     $3, %rdi
        cmp     $4, %rdi
        je      .T1false
        mov     $10, %rdi
        sal     $1, %rdi
        jmp     .T1

.T1false:
        mov     $14, %rdi

.T1: 
        call    print_int

        mov     $2, %rdi
        cmp     $3, %rdi
        sete    %dil
        movzbq  %dil, %rdi
        test    %rdi, %rdi
        jnz     .T2
        mov     $4, %rbx
        mov     $3, %rcx
        sal     $1, %rcx
        cmp     %rbx, %rcx
        setge   %dil
        movzbq  %dil, %rdi



.T2:    call    print_bool
        mov     $0, %rax
        ret


print_int:
        mov     %rdi, %rsi
        mov     $message, %rdi  # arguments pour printf
        mov     $0, %rax
        call    printf
        ret

print_bool:
        cmp     $0, %rdi
        je      .Lfalse
        mov     $true, %rdi
        jmp     .Lprint
.Lfalse:
        mov     $false, %rdi
.Lprint:
        mov     $0, %rax
        call    printf
        ret


        .data
message:.string "%d\n"

true: .string "true\n"

false: .string "false\n"

