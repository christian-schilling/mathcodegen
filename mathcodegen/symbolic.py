from sympy import lambdify, Symbol, N
from expression import Expression
from helper import replace_arguments, map_recursively
import types

# create function wich is evaluated by sympy symbols
# the result is parsed by the Expression class
def symbolic(function):
    def func(*args):
        args = list(args)

        # replace string or Expression arguments by symbols
        # used symbols and corresponding expressions are returned
        args, symargs, expargs = replace_arguments(args, replacer='symbol')

        # create lambda function of symbolic result of the given function
        lambda_function = lambdify(
            symargs,
            map_recursively(N, function(*args)),
            modules=Expression,
            )

        # evaluate expression
        expression = lambda_function(*expargs)

        # create expression type, if neccessary
        if type(expression) not in (list, str, unicode, Expression):
            expression = Expression(expression)

        return expression

    # save original function
    func.function = function

    # create elementwise
    def itersym(self, ctx, *args, **kwargs):
        return iterate_symbolic(ctx, func, *args, **kwargs)

    func.map = types.MethodType(itersym, func, type(func))
    func.elementwise = func.map

    return func

def iterate_symbolic(ctx,func,iterations=1,input=[],output=[],output_indices=None,input_indices=None,assignment='='):
    from pyopencl.elementwise import ElementwiseKernel
    from pyopencl.array import Array

    unique = []
    i=0
    for x in input+output:
        if not hasattr(x,'paramname') and isinstance(x,Array):
            unique.append(x)
            x.paramname = 'param{}'.format(i)
            i+=1

    out_indices = ['i' for x in output]
    if output_indices:
        out_indices = map(str,output_indices(Expression(len(unique[0])),Expression('i'),Expression('iteration')))

    in_indices = ['i' for x in input if hasattr(x,'paramname')]
    if input_indices:
        in_indices = map(str,input_indices(Expression(len(unique[0])),Expression('i'),Expression('iteration')))

    # limit indices to array length
    for i,index in enumerate(in_indices):
        in_indices[i] = '({i}>=0?{i}:0)'.format(i=index)
    for i,index in enumerate(in_indices):
        in_indices[i] = '({i}<{l}?{i}:({l}-1))'.format(i=index,l=len(output[0]))

    # create assignment operator list with same assignment operator for each index if string
    if isinstance(assignment,str):
        assignment = [assignment]*len(output)

    paramlist = ','.join(["float* {}".format(x.paramname) for x in unique])
    code = ';'.join(["float tmp_{}_{}={}[{}]".format(i,x.paramname,x.paramname,ind) for i,ind,x in zip(range(len(input)),in_indices,input) if hasattr(x,'paramname')])
    code += ';'
    code += ';'.join(["{}[{}]{}{{}}".format(x.paramname,i,a,x.paramname) for i,a,x in zip(out_indices,assignment,output)])
    code += ';'
    func_result = func(*['tmp_{}_{}'.format(i,x.paramname) if hasattr(x,'paramname') else x for i,x in enumerate(input)])
    if not isinstance(func_result,list):
        raise ValueError("symbolic function must return a list")
    code = code.format(*func_result)
    code = "for(int iteration=0;iteration<{};iteration++){{{}}}".format(iterations,code)
    kernel = ElementwiseKernel(ctx,paramlist,code,"update")
    def updater(queue=None):
        kernel(*unique)
    updater.code = code
    for x in unique:
        del x.paramname
    return updater

symbolic.map = iterate_symbolic
