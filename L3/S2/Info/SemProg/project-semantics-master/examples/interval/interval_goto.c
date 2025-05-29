/*
 * Cours "Sémantique et Application à la Vérification de programmes"
 *
 * Ecole normale supérieure, Paris, France / CNRS / INRIA
 */

void main(){
  int i = 0;

  if(brand) {
    goto L1;
  }

  L0: // performing a widening here loose all information
  goto LF;

  L1:
  if(brand) {
    i += 1;
  } else {
    i -= 1;
  } // i in [-1; 1]
  goto L0;

  LF:
  assert(i <= 1);
  assert(i >= -1);
}