
class CLExpression:
    def __init__(self,exp):
        self.exp = exp

    def __getitem__(self,key):
        return CLExpression('{}[{}]'.format(self,key))

    def __mul__(self, other):
        return CLExpression('{}*{}'.format(self,other))
    __rmul__ = __mul__

    def __add__(self, other):
        return CLExpression('{}+{}'.format(self,other))
    __radd__ = __add__

    def __sub__(self, other):
        return CLExpression('{}-{}'.format(self,CLExpression(other)))

    def __floordiv__(self, other):
        return CLExpression('(int){}/(int){}'.format(self,other))

    def __rfloordiv__(self, other):
        return CLExpression('(int){}/(int){}'.format(other,self))

    def __truediv__(self, other):
        return CLExpression('{}/{}'.format(self,other))

    def __rtruediv__(self, other):
        return CLExpression('{}/{}'.format(other,self))

    def __div__(self, other):
        return CLExpression('{}/{}'.format(self,other))

    def __rdiv__(self, other):
        return CLExpression('{}/{}'.format(other,self))

    def __mod__(self, other):
        return CLExpression('(int){}%(int){}'.format(self,other))

    def __le__(self,other):
        return CLExpression('{}<={}'.format(self,other))

    def __ge__(self,other):
        return CLExpression('{}>={}'.format(self,other))

    def __lt__(self,other):
        return CLExpression('{}<{}'.format(self,other))

    def __gt__(self,other):
        return CLExpression('{}>{}'.format(self,other))

    def select(self,x,y):
        return CLExpression('{}?{}:{}'.format(self,x,y))

    def assign(self,e):
        return CLExpression('{}={}'.format(self,e))

    def floor(self):
        return CLExpression('floor({})'.format(self))

    def cast(self,t):
        return CLExpression('({}){}'.format(t,self))

    def clip(self,low,high):
        return CLExpression('min(max({},0.0f),1.0f)'.format(self))

    def cos(self):
        return CLExpression('cos({})'.format(self))

    def sin(self):
        return CLExpression('sin({})'.format(self))

    def __str__(self):
        return '({})'.format(self.exp)

    def __pow__(self,other):
        return CLExpression('pow({},{})'.format(self,other))

    def sqrt(self):
        return CLExpression('sqrt({})'.format(self))

    pi = 'M_PI'

def cl_meta(func):
    def f(self,*args):
        newargs = []
        for arg in args:
            if type(arg) is list:
                newargs.append(map(CLExpression,arg))
            else:
                newargs.append(CLExpression(arg))
        args = newargs
        r = func(self,*args)
        if type(r) is list:
            r = ';'.join(map(str,r))
        return r
    return f

def symbolic(func):
    import sympy

    def slugify(s):
        return s.replace(r'[','__').replace(r']','')

    def f(self,*args):
        exprs = {}
        for arg in args:
            if type(arg) is list:
                for a in arg:
                    exprs[sympy.Symbol(slugify(a))] = CLExpression(a)
            else:
                exprs[sympy.Symbol(slugify(arg))] = CLExpression(arg)


        exprs = list(exprs.items())
        symargs = [x for x,y in exprs]
        expargs = [y for x,y in exprs]

        newargs = []
        for arg in args:
            if type(arg) is list:
                na = []
                for a in arg:
                    na.append(sympy.Symbol(slugify(a)))
                newargs.append(na)
            else:
                newargs.append(sympy.Symbol(slugify(arg)))

        f = func(self,*newargs)
        l = sympy.lambdify(symargs,f,CLExpression)
        r = l(*[CLExpression(x) for x in expargs])
        return r
    return f
