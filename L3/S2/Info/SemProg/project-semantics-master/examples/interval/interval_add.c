/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = rand(0, 3);
  int j = rand(-10, 20);
  int x = i + j;
  assert(x >= -10);
  assert(x <= 23);
  assert(x != -10); //@KO
  assert(x != 23); //@KO
}