// pointer1.c
#include <stddef.h>

int main(void)
{
  char x = 0x07;  // allocated on stack
  char *p = NULL; // also allocated on stack...

  p = &x;           // address-of a variable
  *p = *p + 3;      // dereference a pointer
  p = p + 3;        // increment a pointer

  return x; // echo $?
}
