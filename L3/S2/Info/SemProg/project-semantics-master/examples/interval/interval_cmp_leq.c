/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = rand(0, 23);
  if (i <= 10) assert( i <= 12);
  if (i < 0) assert(1 == 0);
}