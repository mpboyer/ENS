#include <stdio.h>
#include <limits.h>
#include <float.h>

int main()
{
  printf("sizeof(char)=%zu [%hhd, %hhd]\n", sizeof(char), CHAR_MIN, CHAR_MAX);
  printf("sizeof(int)=%zu [%d, %d]\n", sizeof(int), INT_MIN, INT_MAX);
  printf("sizeof(unsigned int)=%zu [0, %u]\n", sizeof(unsigned int), UINT_MAX);
  printf("sizeof(double)=%zu [%g, %g]\n", sizeof(double), -FLT_MAX, FLT_MAX);

  return 0;
}

