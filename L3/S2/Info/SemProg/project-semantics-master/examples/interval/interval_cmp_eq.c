/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = rand(0, 42);
  int j = rand(-10, 20);

  if (i == j) {
    assert(i <= 20);
    assert(j >= 0);
    assert(i != 20); //@KO
    assert(j != 0); //@KO
  }
}