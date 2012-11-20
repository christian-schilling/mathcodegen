

class ExpressionMeta(type):
    def __new__(mcs,name,bases,dict):

        operations = dict['operations']
        constants = dict['constants']
        for name,fs in operations:
            def makel(f):
                return lambda *args: args[0].__class__(f.format(
                    *map(args[0].__class__,args)
                ))
            dict[name] = makel(fs)

        cls = type.__new__(mcs,name,bases,dict)

        for name,c in constants:
            setattr(cls,name,cls(c))

        return cls

class CLExpression:
    __metaclass__ = ExpressionMeta

    def __init__(self,exp):
        self.exp = exp

    def __str__(self):
        return '({})'.format(self.exp)

    constants = [
        ('pi','M_PI'),
    ]

    operations = [
        ('__neg__','-{}'),
        ('__sub__','{}-{}'),
        ('__add__','{}+{}'),
        ('__radd__','{1}+{0}'),
        ('__mul__','{}*{}'),
        ('__rmul__','{1}*{0}'),
        ('__div__','{}/{}'),
        ('__rdiv__','{1}/{0}'),
        ('__floordiv__','(int){}/(int){}'),
        ('__rfloordiv__','(int){1}/(int){0}'),
        ('__mod__','(int){}%(int){}'),
        ('__rmod__','(int){1}%(int){0}'),
        ('__truediv__','{}/{}'),
        ('__rtruediv__','{1}/{0}'),
        ('__getitem__','{}[{}]'),
        ('__le__','{}<={}'),
        ('__ge__','{}>={}'),
        ('__lt__','{}<{}'),
        ('__gt__','{}>{}'),
        ('select','{}?{}:{}'),
        ('assign','{}={}'),
        ('cast','({1}){0}'),
        ('floor','floor({})'),
        ('clip','min(max({},(float){}),(float){})'),
        ('cos','cos({})'),
        ('sin','sin({})'),
        ('__pow__','pow({},{})'),
        ('pow','pow({},{})'),
        ('sqrt','sqrt({})'),
        ('gamma','tgamma({})'),
    ]




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
        if isinstance(s,CLExpression):
            s = str(s)
        s = s.replace(r'[','_orbrace_').replace(r']','_crbrace_')
        s = s.replace(r'(','_rbrace_').replace(r')','_cbrace_')
        return s

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
