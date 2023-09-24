#include <stdlib.h>
#include <stdio.h>
#include "matrix.h"
#include <assert.h>

double* matrix_get(matrix m, int p, int q){
    return &(m.values[p * m.columns + q]);
}

matrix matrix_create(int rows, int cols, double val){
    matrix m;
    m.rows = rows;
    m.columns = cols;
    m.values = calloc((cols) * (rows), sizeof(double));
    for (int i = 0; i < rows; i++){
        for (int j = 0; j < cols; j++)
        {
            *matrix_get(m, i, j) = val;
        }
    }
    return m;
}

matrix matrix_identity(int n){
    matrix m;
    m.rows = n;
    m.columns = n;
    m.values = calloc((n)*(n), sizeof(double));
    for (int i = 0; i < n; i++){
        *matrix_get(m, i, i) = 1.;
    }
    return m;
}

void matrix_destroy(matrix m){
    free(m.values);
}

void matrix_print(FILE* out, matrix m){
    for (int i = 0; i < m.rows; i++){
        for (int j = 0; j < m.columns; j++){
            if (j < (m.columns - 1)){
                fprintf(out, "%.2f\t", m.values[i * m.columns + j]);
            }
            else {
                fprintf(out, "%.2f\n", m.values[i * m.columns + j]);
            }
        }
    }    
}

matrix matrix_add(matrix p, matrix q){
    if (p.rows != q.rows || q.columns != p.columns){
        exit;
    }
    matrix m;
    m.rows = p.rows;
    m.columns = p.columns;
    m.values = calloc((p.columns) * (p.rows), sizeof(double));
    for (int i = 0; i < p.rows; i++){
        for (int j = 0; j < p.columns; j++)
        {
            *matrix_get(m, i, j) = *matrix_get(p, i, j) + *matrix_get(q, i, j) ;
        }
    }
    return m;
}


matrix matrix_mul(matrix p, matrix q){
    assert(p.columns != q.rows);
    matrix m;
    m.rows = p.rows;
    m.columns = p.columns;
    for (int i = 0; i < p.rows; i++){
        for (int j = 0; j < q.columns; j++)
        {
            for (int k = 0; k < p.columns; k++){
                *matrix_get(m, i, j) = *matrix_get(p, i, j) + *matrix_get(q, i, j);
            }
                
        }
    }
}
