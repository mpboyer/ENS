/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = 9;
  int j = -2;
  int x = i % j; // a % b = a - b*(a/b)
  assert(x == 1);
}