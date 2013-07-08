from pyopencl.elementwise import ElementwiseKernel
from pyopencl.array import Array
from .. import map as mmap

def map(cl_context, function, iterations=1, input=[], output=[],
    output_indices=None, input_indices=None, assignment='='):
    unique = []
    i=0
    for x in input+output:
        if not hasattr(x,'paramname') and isinstance(x,Array):
            unique.append(x)
            x.paramname = 'param{}'.format(i)
            i+=1

    in_indices = [lambda x, y, z: y] * len(input)
    if input_indices is not None:
        in_indices = [lambda x, y, z: input_indices(x, y, z)[i] for i in range(len(input))]

    out_indices = [lambda x, y, z: y] * len(input)
    if output_indices is not None:
        out_indices = [lambda x, y, z: output_indices(x, y, z)[i] for i in range(len(output))]

    # wrap pyopencl Array to map tuple format
    input = [(x.paramname, len(x), in_indices[i]) \
            if type(x) is Array else x for i, x in enumerate(input)]
    output = [(x.paramname, len(x), out_indices[i]) \
            if type(x) is Array else x for i, x in enumerate(output)]

    paramlist = ','.join(["float* {}".format(x.paramname) for x in unique])
    code = mmap(function, iterations, input, output, assignment)

    kernel = ElementwiseKernel(cl_context, paramlist, code,"update")

    def updater(queue=None):
        kernel(*unique)
    updater.code = code

    for x in unique:
        del x.paramname

    return updater
