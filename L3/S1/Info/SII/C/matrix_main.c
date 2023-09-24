#include <stdlib.h>

#include "matrix.h"

int main(void)
{
  // We consider matrix of double's

  // Create an identity matrix of size 3×3
  matrix m = matrix_identity(3);

  printf("%d %d\n", m.rows, m.columns);
  matrix_print(stdout, m);

  // Create a 3×3 matrix full of 1.'s
  matrix n = matrix_create(3, 3, 1.);

  printf("%d %d\n", n.rows, n.columns);
  matrix_print(stdout, n);

  // Put 42. in the first cell of the matrix n
  *matrix_get(n, 0, 0)=42.;
  matrix_print(stdout, n);

  // Create the matrix r, addition of matrices m and n
  matrix r = matrix_add(m, n);
  printf("%d %d\n", r.rows, r.columns);
  // Display the matrix r
  matrix_print(stdout, r);
  /* The result should be:
   *  43.00   1.00   1.00
       1.00   2.00   1.00
       1.00   1.00   2.00 */

  // Free the memory allocated for all three matrices
  matrix_destroy(m);
  matrix_destroy(n);
  matrix_destroy(r);

  return EXIT_SUCCESS;
}