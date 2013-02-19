

class ExpressionMeta(type):
    def __new__(mcs,name,bases,dict):
        operations = dict['operations']
        constants = dict['constants']
        cls = type.__new__(mcs,name,bases,dict)

        for name,fs in operations:
            def makel(f):
                return lambda *args: cls(f.format(
                    *map(cls,args)
                ))
            setattr(cls,name,makel(fs))


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
        ('cast','{1}({0})'), # brackets will be added because type is an expression
        ('floor','floor({})'),
        ('clip','min(max({},(float){}),(float){})'),
        ('cos','cos({})'),
        ('sin','sin({})'),
        ('__pow__','pow({},{})'),
        ('pow','pow({},{})'),
        ('sqrt','sqrt((float){})'),
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

        s = '({})'.format(s)
        s = s.replace(r'[','_orbrace_').replace(r']','_crbrace_')
        s = s.replace(r'(','_obrace_').replace(r')','_cbrace_')
        s = s.replace(r'{','_ocbrace_').replace(r'}','_ccbrace_')
        s = s.replace(r'*','_mult_').replace(r'+','_plus_')
        s = s.replace(r'-','_minus_').replace(r'/','_div_')
        return 'tmpsymbol_{}'.format(s)

    def f(*args):
        exprs = {}
        for arg in args:
            if type(arg) is list:
                for a in arg:
                    exprs[sympy.Symbol(slugify(a),real=True)] = CLExpression(a)
            elif type(arg) in (str,unicode,CLExpression):
                exprs[sympy.Symbol(slugify(arg),real=True)] = CLExpression(arg)


        exprs = list(exprs.items())
        symargs = [x for x,y in exprs]
        expargs = [y for x,y in exprs]

        newargs = []
        for arg in args:
            if type(arg) is list:
                na = []
                for a in arg:
                    na.append(sympy.Symbol(slugify(a),real=True))
                newargs.append(na)
            elif type(arg) in (str,unicode,CLExpression):
                newargs.append(sympy.Symbol(slugify(arg),real=True))
            else:
                newargs.append(arg)

        symbolic_result = func(*newargs)

        lambdified = sympy.lambdify(symargs,symbolic_result,CLExpression)
        r = lambdified(*[CLExpression(x) for x in expargs])
        return r

    def sy(*args):
        return func(*args)

    def itersym(self,ctx,*args,**kwargs):
        return iterate_symbolic(ctx,f,*args,**kwargs)

    import types
    f.symbolic = sy
    f.map = types.MethodType(itersym,f,type(f))
    f.elementwise = f.map
    return f



def iterate_symbolic(ctx,func,iterations=1,input=[],output=[],output_indices=None,input_indices=None,assignment='='):
    from pyopencl.elementwise import ElementwiseKernel
    from pyopencl.array import Array

    unique = []
    i=0
    for x in input+output:
        if not hasattr(x,'paramname') and isinstance(x,Array):
            unique.append(x)
            x.paramname = 'param{}'.format(i)
            i+=1

    out_indices = ['i' for x in output]
    if output_indices:
        out_indices = map(str,output_indices(CLExpression(len(unique[0])),CLExpression('i'),CLExpression('iteration')))

    in_indices = ['i' for x in input if hasattr(x,'paramname')]
    if input_indices:
        in_indices = map(str,input_indices(CLExpression(len(unique[0])),CLExpression('i'),CLExpression('iteration')))

    for i,index in enumerate(in_indices):
        in_indices[i] = '({i}>=0?{i}:0)'.format(i=index)

    for i,index in enumerate(in_indices):
        in_indices[i] = '({i}<{l}?{i}:({l}-1))'.format(i=index,l=len(output[0]))

    if isinstance(assignment,str):
        assignment = [assignment]*len(output)

    #print in_indices


    paramlist = ','.join(["float* {}".format(x.paramname) for x in unique])
    code = ';'.join(["float tmp_{}_{}={}[{}]".format(i,x.paramname,x.paramname,ind) for i,ind,x in zip(range(len(input)),in_indices,input) if hasattr(x,'paramname')])
    code += ';'
    code += ';'.join(["{}[{}]{}{{}}".format(x.paramname,i,a,x.paramname) for i,a,x in zip(out_indices,assignment,output)])
    code += ';'
    func_result = func(*['tmp_{}_{}'.format(i,x.paramname) if hasattr(x,'paramname') else x for i,x in enumerate(input)])
    if not isinstance(func_result,list):
        raise ValueError("symbolic function must return a list")
    code = code.format(*func_result)
    code = "for(int iteration=0;iteration<{};iteration++){{{}}}".format(iterations,code)
    kernel = ElementwiseKernel(ctx,paramlist,code,"update")
    def updater(queue=None):
        kernel(*unique)
    updater.code = code
    for x in unique:
        del x.paramname
    return updater

symbolic.map = iterate_symbolic
