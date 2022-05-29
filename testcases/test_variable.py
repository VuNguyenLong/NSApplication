import unittest
from io import StringIO

import sys
sys.path.append('F:/ThesisDraft/NSApp/')

import libs.utils as utils

class TestVariable(unittest.TestCase):
    def test_set(self):
        a = utils.Variable()
        a.set(10)
        self.assertTrue(a.data == 10)

    def test_get(self):
        a = utils.Variable()
        a.data = 10
        self.assertTrue(a.get() == 10)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestVariable)

    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(suite)
    print('Tests run ', result.testsRun)
    print('Errors ', result.errors)