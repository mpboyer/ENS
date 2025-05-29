/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = rand(-2, 42);
  assert(i <= 42);
  assert(i >= -2);
  assert(i != 42); //@KO
  assert(i != -2); //@KO
}