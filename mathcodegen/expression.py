class ExpressionMeta(type):
    def __new__(mcs, name, bases, dict):
        # get operations and constants
        operations = dict['operations']
        constants = dict['constants']

        # create class
        cls = type.__new__(mcs, name, bases, dict)

        # create operation methods
        for name, operation in operations:
            # method generator
            def makeMethod(f):
                return lambda self, *args: cls(f.format(self, *map(cls, args)),
                self.recursion_depth + 1, self.subexpression)

            # generate method
            setattr(cls, name, makeMethod(operation))

        # set constants
        for name, constant in constants:
            setattr(cls, name, cls(constant))

        return cls

class Expression:
    __metaclass__ = ExpressionMeta

    def __init__(self, expression, recursion_depth=0, subexpression=None):
        self.expression = expression
        self.recursion_depth = recursion_depth;
        self.subexpression = subexpression

        # shorten expression if recursion depth is above limit
        # this is needed to enable compiler like clang to parse the expressions
        if recursion_depth >= 100:
            self.subexpression = ('subexpression_{}'.format(id(self.expression)),
                Expression(self.expression, recursion_depth - 1, self.subexpression))
            self.expression = self.subexpression[0]
            self.recursion_depth = 0

    def __str__(self):
        return '({})'.format(self.expression)

    # list of constants which are turned into member by ExpressionMeta
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

        if value == 1:
            return self
        else:
            return Expression('{}*{}'.format(
                self, self ** (value - 1)),
                self.recursion_depth + 1, self.subexpression)

    # enrole subexpressions to generate single expression
    def expand(self, dtype='float'):
        # generate list containing list of tuples with subexpression and
        # its name. This list will be reversed order
        subexpressions = []
        expression = self
        while True:
            if expression.subexpression is not None:
                # get subexpression
                subexpressions.append(
                    (expression.subexpression[0],
                        str(expression.subexpression[1])))

                # go one setp deeper
                expression = expression.subexpression[1]
            else:
                break

        # create a compound statement containing all subexpressions
        code = '({\n'
        for expression in reversed(subexpressions):
            code += '{} {} = {};\n'.format(dtype, expression[0], expression[1])
        code += '{};\n}})'.format(self)

        return code
