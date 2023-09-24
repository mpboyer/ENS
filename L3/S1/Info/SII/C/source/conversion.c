#include <stdio.h>

int main()
{
    signed char w = -1; // movb: move byte
    unsigned int x = (unsigned int)w;
    // movsbl: move byte to 'long' with sign extend (no need for cast)

    unsigned int y = (unsigned char)w;
    // movzbl: move byte to 'long' with zero extend

    double z = (double)w;
    // cvtsi2sd: convert integer to double-precision float (no need for cast)

    printf("w=0x%hhx (%hhd) x=0x%08x (%u) y=0x%08x (%u) z=%g\n",
	    w, w, x, x, y, y, z);

    return 0;
}

