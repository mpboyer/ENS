#include <stdio.h>
#include <unistd.h>

#define BUFSIZE 1024

int main(int argc, char *argv[])
{
  char buf[BUFSIZE];

  getcwd(buf, BUFSIZE);
  printf("current working directory=%s\n", buf);

  chdir("/usr/bin");

  getcwd(buf, BUFSIZE);
  printf("current working directory=%s\n", buf);
}

