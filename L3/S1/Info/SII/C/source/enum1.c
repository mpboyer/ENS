#include <stdio.h>

enum suit { diamonds, clubs, hearts, spades };

const char* string_of_suit(enum suit s)
{
    switch (s)
    {
	case diamonds: return "diamonds";
	case clubs:    return "clubs";
	case hearts:   return "hearts";
	case spades:   return "spades";
    }
}

int main(void)
{
    enum suit s = diamonds;

    puts(string_of_suit(s));

    return 0;
}

