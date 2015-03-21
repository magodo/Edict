/*******************************************************/
/* This file includes routines to compute DTW distance */
/*                                                     */
/* Author: Zhaoting Weng 2014                          */
/*******************************************************/

#include "Python.h"
#include "arrayobject.h"
#include "C_dtw.h"

/* ========== Set up the method table ============= */
static PyMethodDef _C_dtwMethods[] = {
    {"dtw", dtw_process, METH_VARARGS},
    {NULL, NULL}
};

/* ========= Initialize the C function =========== */
// Module name must be _C_dtw in compile and linked 
void init_C_dtw()  {
	(void) Py_InitModule("_C_dtw", _C_dtwMethods);
	import_array();  // Must be present for NumPy.  Called first after above line.
}

/* ======== Implement DTW Algorithm  ============
    interface:  dtw_process(mat1, mat2)
        Input: mat1 and mat2 are NumPy matrixes, double type
        Output: a double number                                        */
static PyObject *dtw_process(PyObject *self, PyObject *args)
{
	PyArrayObject *mat1, *mat2;
    double **frameA, **frameB;
	double distance;
	int row1, row2, col1, col2;
	
	/* Parse tuples separately since args will differ between C fcns */
	if (!PyArg_ParseTuple(args, "O!O!", 
		&PyArray_Type, &mat1, &PyArray_Type, &mat2))  return NULL;
	if (NULL == mat1 || NULL == mat2)  return NULL;
	
	/* Check that object input is 'double' type and a matrix
	   Not needed if python wrapper function checks before call to this routine */
	if (not_doublematrix(mat1) || not_doublematrix(mat2)) return NULL;
	
	/* Get the dimensions of the input */
	row1 = mat1->dimensions[0];
	col1 = mat1->dimensions[1];
    row2 = mat2->dimensions[0];
	col2 = mat2->dimensions[1];
    if (col1 != col2) 
    {
        printf("The vector length of each frame is not identical!!!\n");
        return NULL;
    }
	
	/* Change contiguous arrays into C ** arrays (Memory is Allocated!) */
	frameA = pymatrix_to_Carrayptrs(mat1);
	frameB = pymatrix_to_Carrayptrs(mat2);
	
	/* Do the calculation. */
	//...
    //
    printf("FrameA is: %f,...\n", frameA[0][0]);
    //
    //
    
	/* Free memory, close file and return */
	free_Carrayptrs(frameA);
	free_Carrayptrs(frameB);

	return Py_BuildValue("d", distance);
}

/* ==== Check that PyArrayObject is a double (Float) type and a matrix ==============
    return 1 if an error and raise exception */ 
static int  not_doublematrix(PyArrayObject *mat)  
{
	if (mat->descr->type_num != NPY_DOUBLE || mat->nd != 2)  {
		PyErr_SetString(PyExc_ValueError,
			"In not_doublematrix: array must be of type Float and 2 dimensional (n x m).");
		return 1;  }
	return 0;
}

/* ==== Convert python matrix to C array pointers =====
 * Input: Pointer to PyObject, assumed continuous in memory. 
 * Output: Pointer to 2-D arrays.        */
static double **pymatrix_to_Carrayptrs(PyArrayObject *arrayin)
{
    double **c, *a;
    int n, m, i;

    n = arrayin->dimensions[0];
    m = arrayin->dimensions[1];
    a = (double*)arrayin->data;                        // Pointer to arrayin data as double
    c = (double**)malloc(m * sizeof(double*));         // Allocate memory for output pointer
    if (!c)
    {
        printf("Allocation for 2-D array is failed!\n");
        exit(0);
    } 
    for (i = 0; i < n; i++)
    {
        c[i] = a + i*m;
    }

    return c;
}

/* ==== Free a double *vector(vector of pointers) ======= */
static void free_Carrayptrs(double **v)
{
    free(v);
}
