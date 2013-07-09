import pyopencl as cl
from pyopencl.array import Array
from mako.template import Template
from .. import elementwise as melementwise
import os

def elementwise(cl_context, function, iterations=1, input=[],
    output=[], assignment='='):
    # get list of pyopencl arrays in input and output
    # and generate temporary paramter names
    arrays, i = [], 0
    for x in input + output:
        if type(x) in (list, tuple) and not hasattr(x[0], 'paramname'):
            arrays.append(x[0])
            x[0].paramname = 'param{}'.format(i)
            i += 1

        elif type(x) is Array and not hasattr(x, 'paramname'):
            arrays.append(x)
            x.paramname = 'param{}'.format(i)
            i += 1

    # wrap input and output argument list to match mathcodegen elementwise format
    def wrap_pyopencl_arg(arg):
        if type(arg) in (list, tuple) and type(arg[0]) is Array:
            return (arg[0].paramname, len(arg[0]),
                (lambda x, y, z: y) if len(arg) < 2 else arg[1])
        elif type(arg) is Array:
            return (arg.paramname, len(arg), lambda x, y, z: y)
        else:
            return arg

    input = [wrap_pyopencl_arg(arg) for arg in input]
    output = [wrap_pyopencl_arg(arg) for arg in output]

    # generate opencl code with mathcodegen.elementwise function
    # and special kernel template
    code = melementwise(function, iterations, input, output, assignment,
        template=Template(filename=os.path.join(os.path.dirname(__file__),
            'kernel.mako')))

    # build opencl kernel for generated code and define
    # function which executes kernel on the maximum size
    # of the array arguments
    program = cl.Program(cl_context, code).build()
    def updater(queue):
        program.elementwise(queue, (max([len(x) for x in arrays]),),
            None, *[x.data for x in arrays])
    updater.code = code

    # cleanup parameter names for arrays
    for x in arrays:
        del x.paramname

    return updater
