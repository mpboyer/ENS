#include <stdio.h>

// declaration
long factorial(int n);

int main()
{
    int i, j;
    int x = 7;
    char c = 'B';

    if (x > 0) {
      printf("x is positive\n");
    } else if (x < 0) {
      printf("x is negative\n");
    } else {
      printf("x is zero\n");
    }

    switch (c) {
      case 'A':
	printf("c is 'A'\n");
	break;

      case 'B':
	printf("c is 'B'\n");

      case 'C':
	printf("c is 'B' or 'C'\n");
	break;

      default:
	printf("c is not 'A', 'B', or 'C'\n");
    }


    i = 0;
    while (i >= 0) {
      printf("countdown: %d\n", i);
      --i;
    }

    // init;   guard;  after
    for (i = 10; i >= 0; --i) {
      printf("countdown: %d\n", i);
    }

    for (i = 10, j = 0; i >= 0; --i, j++) {
      printf("down: %d up: %d\n", i, j);
    }

    return factorial(7);
}

// definition (and declaration)
long factorial(int n)
{
  if (n == 0)
    return 1;
  else
    return n * factorial(n-1);
}

