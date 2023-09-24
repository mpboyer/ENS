#include "stack.h"
#include <stdlib.h>

struct elem {
  void *x;
  struct elem *link;
};

struct _Stack {
  int count;
  struct elem *head;
};

Stack stack_new(void)
{
  Stack s = malloc(sizeof *s);
  s->count = 0; s->head = NULL;
  return s;
}

void stack_free(Stack s)
{
    free(s->head);
}

