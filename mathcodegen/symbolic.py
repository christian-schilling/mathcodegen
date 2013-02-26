from sympy import lambdify, Symbol
from expression import Expression
import types

# parse symbolic function arguments
def parseArgument(argument, name):
    # string and expression argument
    symbol, expression = None, None
    if type(argument) in (str, unicode, Expression):
        # create symbols
        expression = Expression(argument)
        symbol = Symbol(name, real=True)

        # replace argument by symbol
        argument = symbol

    # list argument
    elif type(argument) is list:
        newarg, symbol, expression = [], [], []
        for i in range(len(argument)):
            # parse argument
            res = parseArgument(argument[i],
                '{}_{}'.format(name, i))

            # add args to lists
            newarg.append(res[0])
            if res[1] is not None:
                symbol += res[1] if type(res[1]) is list else [res[1]]
            if res[2] is not None:
                expression += res[2] if type(res[2]) is list else [res[2]]

        # replace argument by symbols
        argument = newarg

    return argument, symbol, expression

# create symbolic expression
def symbolic(function):
    def func(*args):
        # parse arguments
        args = [arg for arg in args]
        args, symargs, expargs = parseArgument(args, 'tempsymbol')

        # create lambda function
        lambda_function = lambdify(symargs, function(*args),
            modules=Expression)

        # evaluate expression
        expression = lambda_function(*expargs)

        # check type
        if type(expression) not in (list, str, unicode, Expression):
            expression = Expression(expression)

        return expression

    # save function
    func.function = function

    # create elementwise
    def itersym(self,ctx,*args,**kwargs):
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

    for i,index in enumerate(in_indices):
        in_indices[i] = '({i}>=0?{i}:0)'.format(i=index)

    for i,index in enumerate(in_indices):
        in_indices[i] = '({i}<{l}?{i}:({l}-1))'.format(i=index,l=len(output[0]))

    if isinstance(assignment,str):
        assignment = [assignment]*len(output)

    #print in_indices


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
