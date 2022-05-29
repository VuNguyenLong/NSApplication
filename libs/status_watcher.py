from widgets.main_windows import Ui_MainWindow
import libs.utils as utils

from PyQt5.QtWidgets import QMessageBox

class StatusWatcher:
    def __init__(self, ui:Ui_MainWindow, env:utils.Environment, events:utils.Events):
        self.heap = utils.MaxHeap()
        self.ui = ui
        self.env = env

        events.error_event.connect(self.report_error)
        events.warning_event.connect(self.report_warning)
        events.info_event.connect(self.report_info)
        self.events = events

    def get_watch_target(self) -> utils.Task:
        if len(self.heap) > 0:
            return self.heap[0]
        raise Exception('Heap empty')

    def register(self, x:utils.Task):
        x.status_watcher = self
        self.heap.put(x)

    def unregister(self, x:utils.Task):
        self.heap.pop(x)
        self.update_task_status(self.get_watch_target())

    def update_task_status(self, task:utils.Task): # timestamp ~ ID
        current_watch_target = self.get_watch_target()
        if current_watch_target.timestamp == task.timestamp:
            self.update_ui_status_label(task.status)

    def update_ui_status_label(self, new_status):
        self.ui.status.setText(self.env.STATUS_FORMAT.format(new_status))
        if new_status not in [utils.Status.READY]:
            self.ui.status_icon.setVisible(True)
        else:
            self.ui.status_icon.setVisible(False)

    @staticmethod
    def report_error(info):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(info)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    @staticmethod
    def report_warning(info):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(info)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    @staticmethod
    def report_info(info):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(info)
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

