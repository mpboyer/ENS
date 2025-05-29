/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = 0;
  int j = rand(0, 2);
  int x = 0;

  if(i * j == x) {
    assert(j == 0); //@KO
  }
}
