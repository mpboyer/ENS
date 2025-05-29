/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = rand(1, 23);
  int j = rand(5, 42);

  if(i + j > 60) {
    assert(i >= 19);
    assert(j >= 38);
    assert(i != 19); //@KO
    assert(j != 38); //@KO
  }
}