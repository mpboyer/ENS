
// cc -c -S add.c
// see also https://godbolt.org (without Intel ASM syntax)

int iplus(int x, int y)
{
    return x + y;
    // addl	%edx, %eax
    // l = 32-bits
}

char cplus(char x, char y)
{
    return x + y;
    // addl	%edx, %eax
    // l = 32-bit words
}

long lplus(long x, long y)
{
    return x + y;
    // addq	%rdx, %rax
    // q = 64-bit words
}

float fplus(float x, float y)
{
    return x + y;
    // addss	-8(%rbp), %xmm0
    // Scalar Single-Precision FP
}

double dplus(double x, double y)
{
    return x + y;
    // addsd	-16(%rbp), %xmm0
    // Scalar Double-Precision FP
}

