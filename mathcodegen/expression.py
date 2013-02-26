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
                self.depth + 1, self.subexpression)

            # generate method
            setattr(cls, name, makeMethod(operation))

        # set constants
        for name, constant in constants:
            setattr(cls, name, cls(constant))

        return cls

class Expression:
    __metaclass__ = ExpressionMeta

    def __init__(self, expression, depth=0, subexpression=None):
        # save expression
        self.expression = expression

        # recursion depth
        self.depth = depth;

        # create subexpression
        self.subexpression = subexpression

        # shorten expression
        if depth >= 100:
            self.subexpression = ('subexpression_{}'.format(id(self.expression)),
                Expression(self.expression, depth - 1, self.subexpression))
            self.expression = self.subexpression[0]
            self.depth = 0

    def __str__(self):
        return '({})'.format(self.expression)

    # constants
    constants = [
        ('pi', 'M_PI')
    ]

    # operations
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

    def __pow__(self, value):
        if not isinstance(value, int):
            raise self.pow(value)

        if value == 1:
            return self
        else:
            return Expression('{}*{}'.format(
                self, self ** (value - 1)),
                self.depth + 1, self.subexpression)

    def expand(self, dtype='float'):
        # generate subexpressions
        expressions = [('result', str(self.expression))]

        # gather subexpressions
        expression = self
        while True:
            if expression.subexpression is not None:
                # get subexpression
                expressions.append(
                    (expression.subexpression[0],
                        str(expression.subexpression[1])))

                # go one setp deeper
                expression = expression.subexpression[1]
            else:
                break

        # create code
        code = ''
        for expression in reversed(expressions):
            code += '{} {} = {};\n'.format(dtype, expression[0], expression[1])

        return code
