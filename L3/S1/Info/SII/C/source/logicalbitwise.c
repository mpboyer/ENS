#include <stdio.h>

int main()
{
    unsigned int x = 0x6; // 0b1010
    unsigned int y = 0x5; // 0b1001

    printf("x & y = 0x%x; x && y = 0x%x\n", x & y, x && y);
    printf("x | y = 0x%x; x || y = 0x%x\n", x | y, x || y);
    printf(" ~x   = 0x%x;   !x   = 0x%x\n", ~x, !x);
}

