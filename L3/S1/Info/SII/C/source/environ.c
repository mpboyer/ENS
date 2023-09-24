#include <stdio.h>
#include <stdlib.h>

extern char **environ;

int main(int argc, char** argv)
{
  char **pv = environ;

  for (; *pv; ++pv) // *pv != NULL
    printf("%s\n", *pv);

  printf("\n%s\n%s\n", getenv("HOME"),
                         getenv("SHELL"));

  return 0;
}

