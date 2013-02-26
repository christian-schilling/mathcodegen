from expression import Expression

def symbolic(func):
    import sympy

    def slugify(s):
        if isinstance(s,Expression):
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
                    exprs[sympy.Symbol(slugify(a),real=True)] = Expression(a)
            elif type(arg) in (str,unicode,Expression):
                exprs[sympy.Symbol(slugify(arg),real=True)] = Expression(arg)


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
            elif type(arg) in (str,unicode,Expression):
                newargs.append(sympy.Symbol(slugify(arg),real=True))
            else:
                newargs.append(arg)

        symbolic_result = func(*newargs)

        lambdified = sympy.lambdify(symargs,symbolic_result,Expression)
        r = lambdified(*[Expression(x) for x in expargs])
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
        out_indices = map(str,output_indices(Expression(len(unique[0])),Expression('i'),Expression('iteration')))

    in_indices = ['i' for x in input if hasattr(x,'paramname')]
    if input_indices:
        in_indices = map(str,input_indices(Expression(len(unique[0])),Expression('i'),Expression('iteration')))

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
