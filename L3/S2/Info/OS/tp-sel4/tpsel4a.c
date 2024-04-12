/*
 * Determiner si le nombre donne 'n' est premier.
 *
 * Nous renvoyons 0 si 'n' est compose, ou pas-zero si 'n' est premier.
 */
unsigned int is_prime(unsigned int n)
{
    /* Les nombres plus petits que 2 ne sont pas premiers. */
    if (n < 2)
        return 0;

    /* Trouver le premier non insignifiant facteur de 'n'. */
    unsigned int i = 2;
    while (n % i != 0) {
        i++;
    }

    /* Si le premier facteur est 'n' lui-meme, 'n' est premier. */
    return (i == n);
}

