from sympy import lambdify, Symbol
from expression import Expression
from helper import replace_arguments

# create function wich is evaluated by sympy symbols
# the result is parsed by the Expression class
def symbolic(function):
    def func(*args):
        args = list(args)

        # Replace string or Expression arguments by symbols.
        # Used symbols and corresponding expressions are returned.
        args, symargs, expargs = replace_arguments(args, replacer='symbol')

        # create lambda function of symbolic result of the given function
        lambda_function = lambdify(symargs, function(*args),
            modules=Expression)

        # evaluate expression and ensure type of result is Expression
        expression = lambda_function(*expargs)
        if type(expression) not in (list, tuple, str, unicode, Expression):
            expression = Expression(expression)

        return expression

    # save original function
    func.function = function

    return func
