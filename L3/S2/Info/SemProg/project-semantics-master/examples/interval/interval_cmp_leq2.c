/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = rand(1, 23);
  int j = rand(5, 42);
  if(i >= j) {
    assert(i >= 5);
    assert(j <= 23);
    assert(i != 5); //@KO
    assert(j != 23); //@KO
  }
}