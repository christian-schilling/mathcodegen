from sympy import lambdify, Symbol
from expression import Expression
import types

# replaces function arguments recursivly
# generates lists of symbols and expressions and
# replaces strings in argument list by symbols or expressions
def replace_arguments(argument, replacer='symbol',
    symbol_name_base='tmp'):
    # create expression and symbol for string argument
    # replaces argument by symbol or expression
    symbol, expression = None, None
    if type(argument) in (str, unicode, Expression):
        # create expression and symbol for argument
        # to avoid sympy naming conflicts, symbol gets a custom name
        expression = Expression(argument)
        symbol = Symbol(symbol_name_base, real=True)

        # replace argument
        if replacer == 'symbol':
            argument = symbol
        elif replacer == 'expression':
            argument = expression
        else:
            raise ValueError('replacer has to be "symbol" or "expression"')

    # apply replace_arguments recursivly to replace string arguments in
    # nested lists
    elif type(argument) is list:
        newarg, symbol, expression = [], [], []
        for i in range(len(argument)):
            # parse argument recursivly
            arg, symarg, exparg = replace_arguments(
                argument[i], replacer,
                '{}_{}'.format(symbol_name_base, i))
            newarg.append(arg)

            # store generated symbols and expressions in flat list
            if symarg is not None:
                symbol += symarg if type(symarg) is list else [symarg]
            if exparg is not None:
                expression += exparg if type(exparg) is list else [exparg]
        argument = newarg

    return argument, symbol, expression

# evaluates function recursivly on elements
# in nested lists
def map_recursively(function, value):
    if type(value) is list:
        result = []
        for i in range(len(value)):
            res = map_recursively(function, value[i])
            result.append(res)
    else:
        result = function(value)

    return result
