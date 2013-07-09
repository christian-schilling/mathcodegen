from expression import Expression
from expressionize import expressionize
from symbolic import symbolic
from mako.template import Template
import os

# mako template for generating c code
map_template = Template(
    filename=os.path.join(os.path.dirname(__file__), 'templates',
        'elementwise.mako'))

def elementwise(function, iterations=1, input=[], output=[], assignment='=',
    template=map_template, **kargs):
    # evaluate indexing function for each array argument,
    # ensure access within array length, append index to expression
    # and create set of array arguments
    arrays = []
    def eval_indices(arg):
        if type(arg) in (list, tuple):
            index = arg[2] if len(arg) == 3 else lambda n, i, j: i
            name, length = arg[0], arg[1]

            index = expressionize(index)(length, 'i', 'it')
            index = (index >= 0).select(index, 0)
            index = (index < length).select(index, length - 1)

            arg = Expression(name)[index], length
            if (name, length) not in arrays:
                arrays.append((name, length))

        return arg

    input = [eval_indices(arg) for arg in input]
    output = [eval_indices(arg) for arg in output]

    # evaluate function symbolic and create result list if neccessary
    function_result = symbolic(function)(
        *[arg[0] if type(arg) in (list, tuple) else arg for arg in input])
    if type(function_result) not in (list, tuple):
        function_result = [function_result]

    # create code from mako template
    return template.render(
        arrays=list(arrays),
        output=[out[0] for out in output],
        result=[str(res) for res in function_result],
        iterations=iterations,
        assignment=assignment,
        **kargs)
