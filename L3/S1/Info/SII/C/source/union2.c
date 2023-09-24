#include <stdio.h>

enum variant_label { UINT, FLOAT };

typedef struct {
    enum variant_label label;
    union {
      unsigned int d;
      float f;
    };
} variant;

void print(variant v)
{
    switch (v.label)
    {
	case UINT:
	    printf("%u\n", v.d);
	    break;

	case FLOAT:
	    printf("%f\n", v.f);
	    break;
    }
}

int main(void)
{
    variant v1 = { .label = UINT, .d = 77 };
    variant v2 = { .label = FLOAT, .f = 0.3 };

    print(v1);
    print(v2);

    return 0;
}

