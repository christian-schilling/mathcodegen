# creates member and methods for Expression class from lists
# of tuples. The only use of it is to save some lines of code
class ExpressionMeta(type):
    def __new__(mcs, name, bases, dict):
        operations = dict['operations']
        constants = dict['constants']
        cls = type.__new__(mcs, name, bases, dict)

        # create operation methods, all arguments are expected to be
        # compatible with Expression class. Return value is always an
        # Expression
        for name, operation in operations:
            def makeMethod(f):
                def method(*args):
                    # create expessions for all non expression arguments
                    expressions = [arg if type(arg) is cls else cls(arg) for arg in args]

                    # generate new expression with result of operation,
                    # list of all subexpressions and the sum of the recursion depths
                    return cls(f.format(*expressions),
                        reduce(lambda x, y: x+y, [expression.recursion_depth for expression in expressions]),
                        [subexpression for expression in expressions
                            for subexpression in expression.subexpressions
                                if len(expression.subexpressions) != 0])

                return method
            setattr(cls, name, makeMethod(operation))

        # create member of type Expression
        for name, constant in constants:
            setattr(cls, name, cls(constant))

        return cls

# Provides mathematical operations on strings. A recursion depth counter is
# implemented to split expessions with recursion depth above a limit.
# This is needed to avoid recursion depth limitations of c compiler.
class Expression:
    __metaclass__ = ExpressionMeta

    def __init__(self, expression, recursion_depth=1, subexpressions=[]):
        self.expression = expression
        self.recursion_depth = recursion_depth
        self.subexpressions = subexpressions

        # put current expression in to a subexpression and replace expression
        # by its name
        if self.recursion_depth >= 200:
            subexpression = ('subexpression_{}'.format(id(self.expression)), str(self.expression))
            self.subexpressions.append(subexpression)
            self.expression = subexpression[0]
            self.recursion_depth = 1

    def __str__(self):
        return '({})'.format(self.expression)

    # list of constants which are turned into attributes by ExpressionMeta
    constants = [
        ('pi', 'M_PI')
    ]

    # list of operations which are turned into methods by ExpressionMeta
    operations = [
        ('__pos__','+{}'),
        ('__neg__','-{}'),
        ('__sub__','{}-{}'),
        ('__rsub__','{1}-{0}'),
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
        ('__abs__', 'abs({})'),
        ('Abs', 'abs({})'),
        ('__getitem__','{}[{}]'),
        ('__le__','{}<={}'),
        ('__ge__','{}>={}'),
        ('__lt__','{}<{}'),
        ('__gt__','{}>{}'),
        ('select','{}?{}:{}'),
        ('assign','{}={}'),
        ('cast','{1}({0})'),
        ('floor','floor({})'),
        ('clip','min(max({},(float){}),(float){})'),
        ('cos','cos({})'),
        ('sin','sin({})'),
        ('pow','pow({},{})'),
        ('sqrt','sqrt((float){})'),
        ('gamma','tgamma({})'),
    ]

    # pow method expands pow recursivly on int value,
    # or uses built in mathmatical pow for other values
    def __pow__(self, value):
        if not isinstance(value, int):
            return self.pow(value)

        if value < 0:
            return 1.0 / (self ** (-value))
        elif value == 0:
            return Expression(1.0)
        if value == 1:
            return self
        else:
            return self * self ** (value-1)

    # create compound statement containing all subexpressions to 
    # generate single evaluatable expression
    def expand(self, dtype='float'):
        compound_statement = '({\n'
        for subexpression in self.subexpressions:
            compound_statement += '{} {} = {};\n'.format(dtype, subexpression[0], subexpression[1])
        compound_statement += '{};\n}})'.format(self)

        return compound_statement
