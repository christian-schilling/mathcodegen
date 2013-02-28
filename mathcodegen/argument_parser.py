from sympy import lambdify, Symbol
from expression import Expression
import types

# parse function arguments recursivly
# generates lists of symbols and expressions and
# replaces strings in argument list by symbols or expressions
def argumentParser(argument, symbol_name_base,
    argument_replacer='symbol'):
    # create expression and symbol for string argument
    # replaces argument by symbol or expression
    symbol, expression = None, None
    if type(argument) in (str, unicode, Expression):
        # create symbols
        expression = Expression(argument)
        symbol = Symbol(symbol_name_base, real=True)

        # replace argument
        if argument_replacer == 'symbol':
            argument = symbol
        elif argument_replacer == 'expression':
            argument = expression
        else:
            raise ValueError('argument_replacer has to be "symbol" or "expression"')

    # apply argumentParser recursivly to replace string arguments in
    # nested lists
    elif type(argument) is list:
        newarg, symbol, expression = [], [], []
        for i in range(len(argument)):
            # parse argument recursivly
            arg, symarg, exparg = argumentParser(
                argument[i],
                '{}_{}'.format(symbol_name_base, i),
                argument_replacer)
            newarg.append(arg)

            # store generated symbols and expressions in flat list
            if symarg is not None:
                symbol += symarg if type(symarg) is list else [symarg]
            if exparg is not None:
                expression += exparg if type(exparg) is list else [exparg]
        argument = newarg

    return argument, symbol, expression
