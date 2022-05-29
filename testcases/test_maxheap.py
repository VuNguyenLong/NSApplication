import unittest
from io import StringIO

import sys
sys.path.append('F:/ThesisDraft/NSApp/')

import libs.utils as utils

class TestMaxheap(unittest.TestCase):
    def test_put_1(self):
        heap = utils.MaxHeap()
        heap.put(10)
        self.assertTrue(heap.queue == [10])

    def test_put_2(self):
        heap = utils.MaxHeap()
        for i in [10, 3, 5, 11]:
            heap.put(i)
        self.assertTrue(heap.queue == [11, 10, 5, 3])

    def test_put_3(self):
        heap = utils.MaxHeap()
        for i in [10, 3, 5, 11]:
            heap.put(i)
        self.assertTrue(heap.queue == [11, 10, 5, 3])

        heap.pop(5)
        self.assertTrue(heap.queue == [11, 10, 5])

    def test_pop_1(self):
        heap = utils.MaxHeap()
        heap.put(10)
        self.assertTrue(heap.queue == [10])
        heap.pop()
        self.assertTrue(heap.queue == [])

    def test_pop_2(self):
        heap = utils.MaxHeap()
        try:
            heap.pop()
            self.assertTrue(False)
        except IndexError as e:
            self.assertTrue(e == 'index out of range')

if __name__ == '__main__':
    suite = unittest.makeSuite(TestMaxheap)

    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(suite)
    print('Tests run ', result.testsRun)
    print('Errors ', result.errors)