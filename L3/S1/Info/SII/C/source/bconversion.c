
#include <stdio.h>
#include <stdbool.h>

int main()
{
    int x = 0;
    int y = 42;
    int xb = (bool)x;
    int yb = (bool)y;

    printf("xb=%d yb=%d\n", xb, yb);

    return 0;
}

