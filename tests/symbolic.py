import unittest
import mathcodegen
from scipy import weave
import sympy
import numpy

class TestBasicArithmetic(unittest.TestCase):

    def test_add(self):

        @mathcodegen.symbolic
        def adder(a,b):
            return a+b

        self.assertEqual(4,weave.inline('return_val = {};'.format(adder('1','3'))))
        self.assertEqual(9,weave.inline('return_val = {};'.format(adder(2,'7'))))
        self.assertEqual(11,weave.inline('return_val = {};'.format(adder(6,5))))

class TestBoundFunction(unittest.TestCase):
    offset = 5

    @mathcodegen.symbolic
    def adder(self,a,b):
        return a+b+self.offset

    def test_add(self):
        self.assertEqual(5+4,weave.inline('return_val = {};'.format(self.adder('1','3'))))
        self.assertEqual(5+9,weave.inline('return_val = {};'.format(self.adder(2,'7'))))
        self.assertEqual(5+11,weave.inline('return_val = {};'.format(self.adder(6,5))))


class TestConstantParam(unittest.TestCase):

    @mathcodegen.symbolic
    def substituter(self,constant,symbol,expression):
        return expression.subs({'x':constant*symbol})

    def test_substitute(self):
        x = sympy.Symbol('x')
        expression = x**2*sympy.sqrt(3)
        code = 'float b=4;return_val = {};'.format(self.substituter(5,'b',expression))
        self.assertAlmostEqual(numpy.sqrt(3)*(5*4)**2,weave.inline(code))
