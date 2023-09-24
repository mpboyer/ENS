#include <fcntl.h>
#include <unistd.h>

int main(void)
{
    char c;
    while(read(STDIN_FILENO, &c, 1) == 1)
	write(STDOUT_FILENO, &c, 1);

    return 0;
}

