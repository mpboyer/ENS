#include <stdio.h>

enum suit { diamonds = 0, clubs, hearts, spades };

const char* string_of_suit(enum suit s)
{
    static const char* suit_names[] = {
      "diamonds",
      "clubs",
      "hearts",
      "spades"
    };

    return suit_names[s];
}

int main(void)
{
    enum suit s = diamonds;

    puts(string_of_suit(s));

    return 0;
}

