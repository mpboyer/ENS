/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = 1;
  while(rand(0, 1)==0) i++;
  assert(i == 0); //@KO
}