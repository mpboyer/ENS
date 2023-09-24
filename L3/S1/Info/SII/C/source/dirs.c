#include <sys/types.h>
#include <dirent.h>
#include <stdio.h>

int main(int argc, char **argv)
{
  DIR *directory;
  struct dirent *de;

  if (argc <= 1)
      return 1;

  if (!(directory = opendir(argv[1])))
      perror("Failed to open directory");

  while (0 != (de = readdir(directory))) {
      printf("Found file: %s\n", de->d_name);
  }

  closedir(directory);

  return 0;
}

