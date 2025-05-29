/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = 9;
  int j = 0;
  int x = i / j;  // Dividing by zero does not raise an error;
  assert(1 == 2); // test the abstract value is bottom
}
