#ifndef MATRIX_H
#define MATRIX_H
#include <stdlib.h>
#include <stdio.h>

typedef struct {
    int rows;
    int columns;
    double* values;
} matrix;

typedef long int li;
matrix matrix_identity(int n);

matrix matrix_create(int row, int columns, double val);

double* matrix_get(matrix m, int row, int column);

matrix matrix_add(matrix p, matrix q);

void matrix_print(FILE* out, matrix p);

void matrix_destroy(matrix m);

#endif