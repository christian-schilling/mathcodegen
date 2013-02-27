from sympy import lambdify, Symbol
from expression import Expression

def expressionize(func):
    def f(self,*args):
        newargs = []
        for arg in args:
            if type(arg) is list:
                newargs.append(map(Expression,arg))
            else:
                newargs.append(Expression(arg))
        args = newargs
        r = func(self,*args)
        if type(r) is list:
            r = ';'.join(map(str,r))
        return r
    return f

