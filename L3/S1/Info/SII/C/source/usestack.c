#include "stack.h"

int main()
{
    Stack s = stack_new();

    stack_free(s);

    return 0;
}

