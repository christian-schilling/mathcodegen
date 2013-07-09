import unittest
import pyopencl as cl
import pyopencl.array
import mathcodegen
import mathcodegen.pyopencl
import numpy

class TestElementwiseCL(unittest.TestCase):
    def setUp(self):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)

    def tearDown(self):
        del self.queue
        del self.ctx

    def test_elementwise_cl(self):
        def add(a, b):
            return a + b

        A = cl.array.zeros(self.queue, 10, dtype='float32') + 1
        B = cl.array.zeros(self.queue, 10, dtype='float32') + 1
        C = cl.array.zeros(self.queue, 10, dtype='float32') + 1

        adder = mathcodegen.pyopencl.elementwise(self.ctx, add,
            input=[A, B], output=[C])

        adder(self.queue)
        self.assertEqual(list(C.get()), [2.0] * 10)

    def test_elementwise_cl_with_constant(self):
        def add(a, b):
            return a + b

        A = cl.array.zeros(self.queue, 10, dtype='float32') + 1
        C = cl.array.zeros(self.queue, 10, dtype='float32') + 1

        adder = mathcodegen.pyopencl.elementwise(self.ctx, add,
            input=[A, 3], output=[C])

        adder(self.queue)
        self.assertEqual(list(C.get()), [4.0] * 10)

    def test_elementwise_cl_incremental(self):
        def add(a, b):
            return a + b

        A = cl.array.zeros(self.queue, 10, dtype='float32') + 1
        B = cl.array.zeros(self.queue, 10, dtype='float32') + 1
        C = cl.array.zeros(self.queue, 10, dtype='float32')

        adder = mathcodegen.pyopencl.elementwise(self.ctx, add,
            input=[A, B], output=[C], assignment='+=')

        adder(self.queue)
        self.assertEqual(list(C.get()), [2.0] * 10)

        adder(self.queue)
        self.assertEqual(list(C.get()), [4.0] * 10)

    def test_output_is_input(self):
        def add(a, b):
            return a + b

        A = cl.array.zeros(self.queue, 10, dtype='float32') + 1
        B = cl.array.zeros(self.queue, 10, dtype='float32') + 1

        adder = mathcodegen.pyopencl.elementwise(self.ctx, add,
            input=[A, B], output=[A])

        adder(self.queue)
        self.assertEqual(list(A.get()), [2.0] * 10)

    def test_double_input(self):
        def add(a, b):
            return a + b

        A = cl.array.zeros(self.queue, 10, dtype='float32') + 1
        B = cl.array.zeros(self.queue, 10, dtype='float32') + 1

        adder = mathcodegen.pyopencl.elementwise(self.ctx, add,
            input=[A, A], output=[B])

        adder(self.queue)
        self.assertEqual(list(B.get()), [2.0] * 10)

    def test_reverse(self):
        A = cl.array.to_device(self.queue,
            numpy.arange(0, 10).astype('float32'))
        B = cl.array.empty_like(A)

        noper = mathcodegen.pyopencl.elementwise(self.ctx, self.nop,
            input=[A], output=[(B, lambda n, i, j: n - i - 1)],
            iterations=1)

        noper(self.queue)
        self.assertEqual(list(B.get()), range(9, -1, -1))

    def nop(self, a):
        return [a, a*2]

    def test_oddeven(self):
        A = cl.array.to_device(self.queue,
            numpy.array(range(5) * 2).astype('float32'))
        B = cl.array.empty_like(A)
        C = cl.array.empty_like(A)

        noper = mathcodegen.pyopencl.elementwise(self.ctx, self.nop, input=[A],
            output=[
                (B, lambda n, i, j: (2 * i) % n),
                (B, lambda n, i, j: (2 * i + 1) % n)
            ])

        noper(self.queue)
        self.assertEqual(list(B.get()), [0, 0, 1, 2, 2, 4, 3, 6, 4, 8])

    def differece(self, a, b):
        return a - b

    def test_input_indices_diffent_inputs(self):
        A = cl.array.to_device(self.queue,
            numpy.array(range(5) * 2).astype('float32'))
        X = cl.array.to_device(self.queue,
            numpy.array(range(5) * 2).astype('float32'))
        B = cl.array.empty_like(A)

        differ = mathcodegen.pyopencl.elementwise(self.ctx,self.differece,
            input=[(A, lambda n, i, j: i + 1), (X, lambda n, i, j: i - 1)],
            output=[B])

        differ(self.queue)
        self.assertEqual(list(B.get()),
            [1.0, 2.0, 2.0, 2.0,-3.0,-3.0, 2.0, 2.0, 2.0, 1.0])

    def test_input_indices_same_inputs(self):
        A = cl.array.to_device(self.queue,
            numpy.array(range(5)*2).astype('float32'))
        B = cl.array.empty_like(A)

        differ = mathcodegen.pyopencl.elementwise(self.ctx,self.differece,
            input=[(A, lambda n, i, j: i + 1), (A, lambda n, i, j: i - 1)],
            output=[B])

        differ(self.queue)
        self.assertEqual(list(B.get()),
            [1.0, 2.0, 2.0, 2.0, -3.0, -3.0, 2.0, 2.0, 2.0, 1.0])
