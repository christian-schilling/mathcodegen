from sympy import Symbol
from expression import Expression
from helper import map_recursively

# create function which is evaluated by values of Expression type
# string arguments are replaced by Expressions containing holding its value
def expressionize(function):
    def func(*args):
        args = list(args)

        # replace string arguments by values of type Expression
        def argument_replacer(arg):
            return Expression(arg) if type(arg) in (str, unicode) else arg
        args = map_recursively(argument_replacer, args)

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
