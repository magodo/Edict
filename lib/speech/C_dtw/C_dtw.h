/* =============== Python Callable C function ========== */
static PyObject *dtw_process(PyObject*, PyObject*);

/* ===============  Inner C functions ================== */
static int  not_doublematrix(PyArrayObject*);
static double **pymatrix_to_Carrayptrs(PyArrayObject*);
static void free_Carrayptrs(double**);
