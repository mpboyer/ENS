
#include <stdio.h>

// argc = argument count
// argv = argument vector
// sometimes: char *argv[]
int main(int argc, char** argv)
{
  int i;

  for (i = 0; i < argc; i++)
    printf("argument %d: %s\n", i, argv[i]);

  return 0;
}

