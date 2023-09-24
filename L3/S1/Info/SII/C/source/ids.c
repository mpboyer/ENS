#include <stdio.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
  printf("pid=%d\n",  (int)getpid());
  printf("ppid=%d\n", (int)getppid());
  printf("uid=%d\n",  (int)getuid());
  printf("gid=%d\n",  (int)getgid());
}

