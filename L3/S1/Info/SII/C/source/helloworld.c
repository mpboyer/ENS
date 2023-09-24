// helloworld.c
int c = 0;

int puts(const char *s);
void inc(void);

int main(void)
{
  inc();
  inc();
  puts("hello world");

  return c;
}

void inc(void)
{
  c = c + 1;
}

