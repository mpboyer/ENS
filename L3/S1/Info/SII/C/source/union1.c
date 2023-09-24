#include <stdio.h>

// declare a union type
union bytes {
  unsigned int d;
  char bytes[sizeof(int)];
};

int main(void)
{
  union bytes v;

  v.d = 0xABADCAFE;

  printf("v.d=0x%x\n", v.d);
  for (int i = 0; i < sizeof(int); ++i) {
    printf("%hhx\n", v.bytes[i]);
  }

  return 0;
}

