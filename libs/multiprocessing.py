from PyQt5.QtCore import QThread
import libs.utils as utils

class FunctionalThread(QThread):
    def __init__(self, task:utils.Task, parent=None):
        super(FunctionalThread, self).__init__(parent)
        self.task = task
        self.task.status = utils.Status.READY

    def run(self):
        try:
            #print('Thread ', self.task.timestamp)
            self.task.update_status(utils.Status.ACQUIRE)
            assert (self.task.acquire() == utils.ReturnCode.S_OK, 'ACQUIRE_ERROR')

            self.task.update_status(utils.Status.PROCESSING)
            assert (self.task.functional(**self.task.kwargs) == utils.ReturnCode.S_OK, 'FUNCTIONAL_ERROR')

            self.task.update_status(utils.Status.RELEASE)
            assert (self.task.release() == utils.ReturnCode.S_OK, 'RELEASE_ERROR')

            self.task.update_status(utils.Status.EXIT)
            #print('Thread {} unregistered'.format(self.task.timestamp))

            self.task.callback()
            self.unregister_status_watcher()
        except Exception as e:
            print(e)
            assert (
                self.task.release() == utils.ReturnCode.S_OK,
                f'RELEASE_ERROR in task id {self.task.timestamp}'
            )
            self.task.update_status(utils.Status.TERMINATE)
            self.unregister_status_watcher()
            self.exit(utils.ReturnCode.FAILED)
            return

        self.exit(utils.ReturnCode.S_OK)

    def unregister_status_watcher(self):
        self.task.status_watcher.unregister(self.task)
