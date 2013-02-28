from sympy import lambdify, Symbol
from expression import Expression
from argument_parser import argumentParser

# create function which is evaluated by values of Expression type
def expressionize(function):
    def func(*args):
        args = list(args)

        # replace string arguments by values of type Expression
        args, _, _ = argumentParser(args, 'tempsymbol',
            argument_replacer='expression')

        # evaluate expression
        expression = function(*args)

        # concacate expression lists
        if type(expression) is list:
            expression = ';'.join(map(str, expression))

        # create values of type expression, if neccessary
        elif type(expression) not in (str, unicode, Expression):
            expression = Expression(expression)

        return expression
    return func
