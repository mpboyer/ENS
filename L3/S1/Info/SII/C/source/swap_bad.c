
void swap(int x, int y);

int main()
{
  int a = 1;
  int b = 2;

  swap(a, b);

  return b;
}

void swap(int x, int y)
{
  int temp;

  temp = x;
  x = y;
  y = temp;
}

