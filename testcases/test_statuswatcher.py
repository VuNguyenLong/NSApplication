import unittest
from io import StringIO
import time
import numpy as np
from functools import *

import sys
sys.path.append('F:/ThesisDraft/NSApp/')

import libs.utils as utils
import libs.status_watcher as status_watcher


class Ui_MainWindow:
    class Text:
        def __init__(self):
            self.t = None

        def setText(self, x):
            self.t = x

    class Icon:
        def __init__(self):
            self.v = None

        def setVisible(self, x):
            self.v = x

    def __init__(self):
        self.status = Ui_MainWindow.Text()
        self.status_icon = Ui_MainWindow.Icon()

class TestStatusWatcher(unittest.TestCase):
    def test_register_1(self):
        ui = Ui_MainWindow()
        env = utils.Environment()
        events = utils.Events()
        watcher = status_watcher.StatusWatcher(ui, env, events)
        delays = [1, 0.1, 0.5, 2, 0.8]

        for i in range(5):
            watcher.register(utils.Task())
            time.sleep(delays[i])

        self.assertTrue(watcher.heap[0] == np.max(watcher.heap.queue))

    def test_register_2(self):
        ui = Ui_MainWindow()
        env = utils.Environment()
        events = utils.Events()
        watcher = status_watcher.StatusWatcher(ui, env, events)
        delays = [1, 0.1, 0.5, 2, 0.8]

        tasks = []

        for i in range(5):
            task = utils.Task()
            watcher.register(task)
            tasks.append(task)
            time.sleep(delays[i])

        self.assertTrue(watcher.heap[0] == np.max(watcher.heap.queue))

        for i in range(2):
            watcher.unregister(tasks[-i])
            self.assertFalse(tasks[-i] in watcher.heap.queue)

        self.assertFalse(watcher.heap[0] == tasks[-1])
        self.assertTrue(watcher.heap[0] == tasks[-3])

    def test_register_3(self):
        ui = Ui_MainWindow()
        env = utils.Environment()
        events = utils.Events()
        watcher = status_watcher.StatusWatcher(ui, env, events)

        try:
            watcher.unregister(utils.Task())
            self.assertTrue(False)
        except Exception as e:
            self.assertTrue(e == 'Heap empty')


if __name__ == '__main__':
    suite = unittest.makeSuite(TestStatusWatcher)

    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(suite)
    print('Tests run ', result.testsRun)
    print('Errors ', result.errors)