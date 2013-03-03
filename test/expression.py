import unittest
import mathcodegen
from scipy import weave


class TestSubexpressions(unittest.TestCase):
    def test_subexpressions(self):
        @mathcodegen.expressionize
        def mul(x, y):
            if y <= 1:
                return x
            else:
                return x + mul(x, y - 1)

        # decreas recursion limit masively
        max_recursion_depth = mathcodegen.Expression.max_recursion_depth
        mathcodegen.Expression.max_recursion_depth = 5

        code = 'return_val = {};'.format(mul('7', 10).expand())
        self.assertEqual(7 * 10, weave.inline(code))

        # reset recursion limit
        mathcodegen.Expression.max_recursion_depth = max_recursion_depth
