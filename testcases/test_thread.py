import unittest
from io import StringIO
import time

import sys
sys.path.append('F:/ThesisDraft/NSApp/')

import libs.utils as utils
import libs.status_watcher as status_watcher
import libs.multiprocessing as multiprocessing

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

class Task_1(utils.Task):
    def acquire(self):
        return utils.ReturnCode.FAILED

    def functional(self, **kwargs):
        pass

    def release(self):
        pass

class Task_2(utils.Task):
    def acquire(self):
        pass

    def functional(self):
        return utils.ReturnCode.FAILED

    def release(self):
        pass

class Task_3(utils.Task):
    def acquire(self):
        pass

    def functional(self, **kwargs):
        pass

    def release(self):
        return utils.ReturnCode.FAILED

class Task_4(utils.Task):
    def acquire(self):
        pass

    def functional(self, **kwargs):
        pass

    def release(self):
        pass

    def callback(self):
        raise Exception('Callback failed')


class Task_5(utils.Task):
    def acquire(self):
        pass

    def functional(self, **kwargs):
        pass

    def release(self):
        pass


class TestThread(unittest.TestCase):
    def test_task_1(self):
        ui = Ui_MainWindow()
        env = utils.Environment()
        events = utils.Events()
        watcher = status_watcher.StatusWatcher(ui, env, events)
        task0 = Task_1()
        task1 = Task_1()
        watcher.register(task0)
        watcher.register(task1)
        thread = multiprocessing.FunctionalThread(task0)
        thread.start()

        while not thread.isFinished():
            time.sleep(0.1)

        self.assertTrue(thread.task.status == utils.Status.TERMINATE)

    def test_task_2(self):
        ui = Ui_MainWindow()
        env = utils.Environment()
        events = utils.Events()
        watcher = status_watcher.StatusWatcher(ui, env, events)
        task0 = Task_2()
        task1 = Task_2()
        watcher.register(task0)
        watcher.register(task1)
        thread = multiprocessing.FunctionalThread(task0)
        thread.start()

        while not thread.isFinished():
            time.sleep(0.1)

        self.assertTrue(thread.task.status == utils.Status.TERMINATE)

    def test_task_3(self):
        ui = Ui_MainWindow()
        env = utils.Environment()
        events = utils.Events()
        watcher = status_watcher.StatusWatcher(ui, env, events)
        task0 = Task_3()
        task1 = Task_3()
        watcher.register(task0)
        watcher.register(task1)
        thread = multiprocessing.FunctionalThread(task0)
        thread.start()

        while not thread.isFinished():
            time.sleep(0.1)

        self.assertTrue(thread.task.status == utils.Status.TERMINATE)

    def test_task_4(self):
        ui = Ui_MainWindow()
        env = utils.Environment()
        events = utils.Events()
        watcher = status_watcher.StatusWatcher(ui, env, events)
        task0 = Task_4()
        task1 = Task_4()
        watcher.register(task0)
        watcher.register(task1)
        thread = multiprocessing.FunctionalThread(task0)
        thread.start()

        while not thread.isFinished():
            time.sleep(0.1)

        self.assertTrue(thread.task.status == utils.Status.TERMINATE)

    def test_task_5(self):
        ui = Ui_MainWindow()
        env = utils.Environment()
        events = utils.Events()
        watcher = status_watcher.StatusWatcher(ui, env, events)
        task0 = Task_5()
        task1 = Task_5()
        watcher.register(task0)
        watcher.register(task1)
        thread = multiprocessing.FunctionalThread(task0)
        thread.start()

        while not thread.isFinished():
            time.sleep(0.1)

        self.assertTrue(thread.task.status == utils.Status.TERMINATE)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestThread)

    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(suite)
    print('Tests run ', result.testsRun)
    print('Errors ', result.errors)