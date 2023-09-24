
typedef struct _Stack *Stack;

Stack stack_new(void);
void stack_push(Stack s, void *v);
void *stack_pop(Stack s);
void stack_free(Stack s);

