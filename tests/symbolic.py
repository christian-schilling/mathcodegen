import unittest
import cl_meta
from scipy import weave

class TestBasicArithmetic(unittest.TestCase):

    def test_add(self):

        @cl_meta.symbolic
        def adder(a,b):
            return a+b

        self.assertEqual(4,weave.inline('return_val = {};'.format(adder('1','3'))))
        self.assertEqual(9,weave.inline('return_val = {};'.format(adder(2,'7'))))
        self.assertEqual(11,weave.inline('return_val = {};'.format(adder(6,5))))

class TestBoundFunction(unittest.TestCase):
    offset = 5

    @cl_meta.symbolic
    def adder(self,a,b):
        return a+b+self.offset

    def test_add(self):
        self.assertEqual(5+4,weave.inline('return_val = {};'.format(self.adder('1','3'))))
        self.assertEqual(5+9,weave.inline('return_val = {};'.format(self.adder(2,'7'))))
        self.assertEqual(5+11,weave.inline('return_val = {};'.format(self.adder(6,5))))


