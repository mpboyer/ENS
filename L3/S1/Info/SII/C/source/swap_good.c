
void swap(int *x, int *y);

int main()
{
  int a = 1;
  int b = 2;

  swap(&a, &b);

  return b;
}

void swap(int *px, int *py)
{
  int temp;

  temp = *px;
  *px = *py;
  *py = temp;
}

