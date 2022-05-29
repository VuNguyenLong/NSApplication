import time
from widgets.main_windows import Ui_MainWindow
from widgets.recording_form import Ui_Form
from widgets.media import RecordDisplayPanel
from libs.fileops import FileDialog
import libs.utils as utils
import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui, QtWidgets, QtCore
import librosa
import sounddevice as sd

class ImportFile(utils.Task):
    def __init__(self, filepath, ui:Ui_MainWindow, env:utils.Environment):
        super(ImportFile, self).__init__()
        self.ui = ui
        self.env = env
        self.filepath = filepath

    def acquire(self):
        self.ui.inputs_box.setEnabled(False)
        return utils.ReturnCode.S_OK

    def release(self):
        self.ui.inputs_box.setEnabled(True)
        return utils.ReturnCode.S_OK

    def functional(self, **kwargs):
        try:
            self.update_status(utils.Status.Inputs.LOADING)
            sound, _ = librosa.load(
                self.filepath,
                sr=self.env.SAMPLE_RATE
            )
            self.env.input_data.set(np.array(sound))
        except Exception as e:
            self.last_error = e
            self.status_watcher.events.error_event.emit(str(e))
            return utils.ReturnCode.FAILED
        return utils.ReturnCode.S_OK

    def callback(self):
        self.ui.original_sound.show()



class RecordingForm(QWidget):
    def __init__(self, ui:Ui_MainWindow, env:utils.Environment, parent=None):
        super(RecordingForm, self).__init__(parent=parent)
        self.ui                     = ui
        self.env                    = env
        self.task                   = None
        self.queue                  = []
        self.widget_queue           = []
        self.pause_signal           = True
        self.widget_timer           = QtCore.QTimer(self)
        self.form_ui                = Ui_Form()

        self.form_ui.setupUi(self)
        self.form_ui.retranslateUi(self)
        self.create_display_widget()
        self.env.record_cache.set(None)

        self.form_ui.play_pause_btn.clicked.connect(self.__continue_pause__)
        self.form_ui.stop_btn.clicked.connect(self.__stop__)
        self.widget_timer.start(400)

    def create_display_widget(self):
        self.form_ui.play_pause_btn = utils.PushButton(self, use_border=False, bg_change=False, circular=True)
        self.form_ui.play_pause_btn.setGeometry(QtCore.QRect(230, 260, 32, 32))
        self.form_ui.play_pause_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/play"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.form_ui.play_pause_btn.setIcon(icon1)
        self.form_ui.play_pause_btn.setIconSize(QtCore.QSize(16, 16))
        self.form_ui.play_pause_btn.setObjectName("play_pause_btn")

        self.form_ui.stop_btn = utils.PushButton(self, use_border=False, bg_change=False, circular=True)
        self.form_ui.stop_btn.setGeometry(QtCore.QRect(290, 260, 32, 32))
        self.form_ui.stop_btn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/stop"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.form_ui.stop_btn.setIcon(icon2)
        self.form_ui.stop_btn.setIconSize(QtCore.QSize(16, 16))
        self.form_ui.stop_btn.setObjectName("stop_btn")

        self.form_ui.widget = RecordDisplayPanel(self.env.record_cache, parent=self)
        self.form_ui.widget.setGeometry(QtCore.QRect(10, 10, 511, 241))
        self.form_ui.widget.setObjectName("widget")

        self.widget_timer.timeout.connect(self.form_ui.widget.show)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.task.exit_signal = True
        self.widget_timer.stop()

    def __pause__(self):
        self.pause_signal = True
        new_icon = QtGui.QIcon(":/icons/play")
        self.form_ui.play_pause_btn.setIcon(new_icon)

    def __continue__(self):
        self.pause_signal = False
        new_icon = QtGui.QIcon(":/icons/pause")
        self.form_ui.play_pause_btn.setIcon(new_icon)

    def __continue_pause__(self):
        if self.pause_signal:
            self.__continue__()
        else:
            self.__pause__()

    def __stop__(self):
        self.close()


class RecordingTask(utils.Task):
    def __init__(self, ui:Ui_MainWindow, env:utils.Environment, recording_form:RecordingForm):
        super(RecordingTask, self).__init__()
        self.ui = ui
        self.env = env
        self.form = recording_form
        self.form.task = self
        self.exit_signal = False

    def __callback__(self, indata, frames, _time, status):
        if not self.form.pause_signal:
            self.form.queue.extend(indata.reshape(-1))
            if len(self.form.widget_queue) > 4 * indata.shape[0]:
                self.form.widget_queue.extend(indata.reshape(-1))
                self.form.widget_queue = self.form.widget_queue[indata.shape[0]:]
            else:
                self.form.widget_queue.extend(indata.reshape(-1))
            self.env.record_cache.set(np.array(self.form.widget_queue))

    def acquire(self):
        self.ui.record_btn.setEnabled(False)
        return utils.ReturnCode.S_OK

    def release(self):
        self.ui.record_btn.setEnabled(True)
        return utils.ReturnCode.S_OK

    def functional(self, **kwargs):
        try:
            stream = sd.InputStream(
                device=self.form.env.mic.get(),
                channels=1,
                samplerate=utils.Environment.SAMPLE_RATE,
                latency=0.1, # 100ms
                callback=self.__callback__
            )
            self.update_status(utils.Status.Inputs.RECORDING)

            with stream:
                while not self.exit_signal:
                    QtCore.QThread.usleep(utils.Environment.WAITING_RECORD_INTERVAL * 1000)
            if len(self.form.queue) > 0:
                self.env.input_data.set(np.array(self.form.queue))

        except Exception as e:
            self.last_error = e
            self.status_watcher.events.error_event.emit(str(e))
            return utils.ReturnCode.FAILED
        return utils.ReturnCode.S_OK

    def callback(self):
        if len(self.form.queue) > 0:
            self.ui.original_sound.show()


# handle inputs group function
class Inputs:
    def __init__(self, ui:Ui_MainWindow, file_dialog:FileDialog, env:utils.Environment):
        self.ui = ui
        self.env = env
        self.file_dialog = file_dialog

        self.form = None

    def create_import_task(self):
        filepath = self.file_dialog.open_file(['*.wav'])
        if filepath == '':
            return None
        return ImportFile(filepath, self.ui, self.env)

    def create_recording_task(self):
        self.form = RecordingForm(self.ui, self.env)
        self.form.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.form.show()
        return RecordingTask(self.ui, self.env, self.form)