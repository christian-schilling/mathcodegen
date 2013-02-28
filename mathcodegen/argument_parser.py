from sympy import lambdify, Symbol
from expression import Expression
import types

# parse symbolic function arguments recursivly.
# generates lists of symbols and expressions and
# replaces strings in argument list by symbols
def argumentParser(argument, symbol_name_base,
    argument_replacer='symbol'):
    # string and expression argument
    symbol, expression = None, None
    if type(argument) in (str, unicode, Expression):
        # create symbols
        expression = Expression(argument)
        symbol = Symbol(symbol_name_base, real=True)

        # replace argument by symbol
        if argument_replacer == 'symbol':
            argument = symbol
        elif argument_replacer == 'expression':
            argument = expression
        else:
            raise ValueError('argument_replacer has to be "symbol" or "expression"')

    # list argument
    elif type(argument) is list:
        newarg, symbol, expression = [], [], []
        for i in range(len(argument)):
            # parse argument
            res = argumentParser(
                argument[i],
                '{}_{}'.format(symbol_name_base, i),
                argument_replacer)

            # add args to lists
            newarg.append(res[0])
            if res[1] is not None:
                symbol += res[1] if type(res[1]) is list else [res[1]]
            if res[2] is not None:
                expression += res[2] if type(res[2]) is list else [res[2]]

        # replace argument by symbols
        argument = newarg
    return argument, symbol, expression
