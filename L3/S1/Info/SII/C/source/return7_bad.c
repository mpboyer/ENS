
int *f(void);

int main()
{
  int *px;

  px = f();

  return *px;
}

int *f(void)
{
  int x = 7;

  return &x;
}

