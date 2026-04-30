#include <Python.h>
#include <numpy/arrayobject.h>
#include <networkx/graph.h>

static PyObject* find_initPaths(PyObject* self, PyObject* args) {
    PyArrayObject* fullPathGraph;
    int num_of_true_node_index;

    if (!PyArg_ParseTuple(args, "Oi", &fullPathGraph, &num_of_true_node_index)) {
        return NULL;
    }

    int n_dims = PyArray_NDIM(fullPathGraph);
    npy_intp* dims = PyArray_DIMS(fullPathGraph);
    int* data = (int*) PyArray_DATA(fullPathGraph);

    PyObject* update_path = PyList_New(0);

    printf("Total nodes: %d\n", num_of_true_node_index);

    for (int i = 1; i < num_of_true_node_index; i++) {
        char completed_num[20];
        sprintf(completed_num, "%.5f%%", ((float)i/num_of_true_node_index) * 100);
        printf("%s completed\n", completed_num);

        for (int j = i + 1; j < num_of_true_node_index + 1; j++) {
            try {
                int path_length;
                int* path = shortest_path(data, n_dims, dims, i, j, &path_length);
                if (initPaths_continuity_check(path, path_length) == true) {
                    PyList_Append(update_path, Py_BuildValue("(ii)", i, j));
                }
            } catch (const networkx::exception& e) {
                // Ignore no path exceptions
            }
        }
    }

    return update_path;
}

static PyMethodDef methods[] = {
    {"find_initPaths", find_initPaths, METH_VARARGS, "Find connections between true nodes."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "example",
    "Example module",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_example(void) {
    import_array();  // Import NumPy array module
    return PyModule_Create(&module);
}
