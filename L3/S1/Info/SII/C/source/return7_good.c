#include <stdlib.h>

int *f(void);

int main()
{
  int *px;
  int x;

  px = f();
  x = *px;
  free(px);

  return x;
}

int *f(void)
{
  int *pi = malloc(sizeof(int));
  *pi = 7;

  return pi;
}

