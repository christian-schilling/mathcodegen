from sympy import lambdify, Symbol
from expression import Expression

# replaces function arguments recursively
# generates lists of symbols and expressions and
# replaces strings in argument list by symbols
def replace_arguments(argument, symbol_name_base='tmp'):
    # create expression and symbol for string argument
    # replaces argument by symbol or expression
    # to avoid sympy naming conflicts, symbol gets a custom name
    symbol, expression = None, None
    if type(argument) in (str, unicode, Expression):
        expression = argument if type(argument) is Expression else Expression(argument)
        symbol = Symbol(symbol_name_base, real=True)
        argument = symbol

    # apply replace_arguments recursivly to replace string or expression
    # arguments in nested lists
    elif type(argument) is list:
        newarg, symbol, expression = [], [], []
        for i in range(len(argument)):
            arg, symarg, exparg = replace_arguments(
                argument[i], '{}_{}'.format(symbol_name_base, i))
            newarg.append(arg)

            # store generated symbols and expressions in flat list
            if symarg is not None:
                symbol += symarg if type(symarg) is list else [symarg]
            if exparg is not None:
                expression += exparg if type(exparg) is list else [exparg]
        argument = newarg

    return argument, symbol, expression

# create function wich is evaluated by sympy symbols
# the result is parsed by the Expression class
def symbolic(function):
    def func(*args):
        args = list(args)

        # Replace string or Expression arguments by symbols.
        # Used symbols and corresponding expressions are returned.
        args, symargs, expargs = replace_arguments(args)

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
