#define PY_SSIZE_T_CLEAN
#include <errno.h>
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "i2c_tools.h"


static PyObject* py_i2c_open_bus(PyObject* self, PyObject* args) {
    const char* bus_path;
    if (!PyArg_ParseTuple(args, "s", &bus_path)) {
        return NULL;
    }

    int fd = i2c_bus(bus_path);
    if (fd < 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL; // Error already printed by i2c_bus
    }

    return PyLong_FromLong(fd);
}


static PyObject* py_i2c_read_byte(PyObject* self, PyObject* args) {
    int bus;
    uint8_t slave_addr, register_addr;

    if (!PyArg_ParseTuple(args, "iBB", &bus, &slave_addr, &register_addr)) {
        return NULL;
    }

    int register_value;
    Py_BEGIN_ALLOW_THREADS
    register_value = i2c_read_byte(bus, slave_addr, register_addr);
    Py_END_ALLOW_THREADS

    if (register_value < 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL; // Error already printed by i2c_read_byte
    }

    return PyLong_FromLong(register_value);
}


static PyObject* py_i2c_write_byte(PyObject* self, PyObject* args) {
    int bus;
    uint8_t slave_addr, register_addr, value;

    if (!PyArg_ParseTuple(args, "iBBB", &bus, &slave_addr, &register_addr, &value)) {
        return NULL;
    }

    int rtn;
    Py_BEGIN_ALLOW_THREADS
    rtn = i2c_write_byte(bus, slave_addr, register_addr, value);
    Py_END_ALLOW_THREADS

    if (rtn < 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL; // Error already printed by i2c_write_byte
    }

    Py_RETURN_NONE;
}


static PyObject* py_close_bus(PyObject* self, PyObject* args) {
    int bus;
    if (!PyArg_ParseTuple(args, "i", &bus)) {
        return NULL;
    }

    if (close(bus) < 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    Py_RETURN_NONE;
}


static PyMethodDef pi2c_tools_methods[] = {
    {"i2c_open_bus", py_i2c_open_bus, METH_VARARGS, "Open an I2C bus and return its file descriptor."},
    {"i2c_read_byte", py_i2c_read_byte, METH_VARARGS, "Read a byte from a specified register of an I2C device."},
    {"i2c_write_byte", py_i2c_write_byte, METH_VARARGS, "Write a byte to a specified register of an I2C device."},
    {"i2c_close_bus", py_close_bus, METH_VARARGS, "Close an I2C bus."},
    {NULL, NULL, 0, NULL} // Sentinel
};


static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "pi2c_tools",
    "Python bindings for C-based I2C communication on Raspberry Pi.",
    -1,
    pi2c_tools_methods
};


PyMODINIT_FUNC PyInit_pi2c_tools(void) {
    return PyModule_Create(&moduledef);
}