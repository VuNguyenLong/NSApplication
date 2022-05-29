from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

plt.ion()

import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
import librosa
import librosa.display
import sounddevice as sd
import libs.utils as utils
from widgets.main_windows import Ui_MainWindow


class SoundDisplayPanel(FigureCanvas, QtWidgets.QWidget):
    def __init__(self, config:utils.Config.DisplayConfig, parent=None, panel_size=None, dpi=100, play_on_click=True):
        self.figure             = Figure(figsize=panel_size, dpi=dpi, facecolor='white')
        super().__init__(self.figure)

        self.axis               = None
        self.config             = config
        self.is_playing         = False
        self.play_on_click      = play_on_click

        self.setParent(parent)

    def show(self):
        if self.config.data_src.get() is None:
            return
        self.figure.clf()
        self.axis = self.figure.add_subplot(111)

        self.axis.set_aspect('auto')
        self.axis.spines['top'].set_visible(False)
        self.axis.spines['right'].set_visible(False)

        self.axis.xaxis.get_label().set_visible(False)
        self.axis.yaxis.get_label().set_visible(False)
        self.axis.tick_params(labelsize=8)

        if self.config.view_mode.get() == utils.ViewMode.WAVEFORM:
            librosa.display.waveshow(
                self.config.data_src.get(),
                sr=utils.Environment.SAMPLE_RATE,
                ax=self.axis,
                x_axis='s'
            )

        elif self.config.view_mode.get() == utils.ViewMode.SPECTRUM:
            nfft = self.config.spectrum_config.nfft.get()
            spectrum = np.fft.fft(
                self.config.data_src.get(),
                n=nfft
            )
            self.axis.plot(np.arange(-nfft/2, nfft/2, 1), np.abs(spectrum))

        elif self.config.view_mode.get() == utils.ViewMode.SPECTROGRAM:
            stft = librosa.stft(
                self.config.data_src.get(),
                n_fft=self.config.spectrogram_config.nfft.get(),
                window=self.config.spectrogram_config.window_type.get(),
                hop_length=self.config.spectrogram_config.hop_length.get(),
                win_length=self.config.spectrogram_config.win_length.get()
            )

            if self.config.spectrogram_config.abs2db.get():
                _stft = librosa.amplitude_to_db(
                    np.abs(stft),
                    ref=np.max
                )
            else:
                _stft = np.abs(stft)

            librosa.display.specshow(
                _stft,
                ax=self.axis,
                x_axis='s',
                y_axis='fft',

                n_fft=self.config.spectrogram_config.nfft.get(),
                hop_length=self.config.spectrogram_config.hop_length.get(),
                win_length=self.config.spectrogram_config.win_length.get(),
                sr=utils.Environment.SAMPLE_RATE
            )

        else:
            raise Exception('Not a valid view mode')

        self.figure.tight_layout()
        self.figure.canvas.draw()

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        if not self.play_on_click:
            return
        if a0.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.config.data_src.get() is not None:
                sd.stop()
                if not self.is_playing:
                    sd.play(self.config.data_src.get(), samplerate=utils.Environment.SAMPLE_RATE)
                self.is_playing = not self.is_playing


class RecordDisplayPanel(FigureCanvas, QtWidgets.QWidget):
    def __init__(self, data_src:utils.Variable, parent=None, panel_size=None, dpi=100, play_on_click=True):
        self.figure = Figure(figsize=panel_size, dpi=dpi, facecolor='white')
        super().__init__(self.figure)

        self.axis = None
        self.data_src = data_src
        self.is_playing = False
        self.play_on_click = play_on_click

        self.setParent(parent)

    def show(self):
        if self.data_src.get() is None:
            return
        self.figure.clf()
        self.axis = self.figure.add_subplot(111)

        self.axis.set_aspect('auto')
        self.axis.spines['top'].set_visible(False)
        self.axis.spines['right'].set_visible(False)
        self.axis.spines['bottom'].set_visible(False)

        self.axis.xaxis.get_label().set_visible(False)
        self.axis.yaxis.get_label().set_visible(False)
        self.axis.tick_params(labelsize=8)
        self.axis.set_xticks([])

        self.axis.set_ylim(-1, 1)
        self.axis.plot(self.data_src.get())

        self.figure.tight_layout()
        self.figure.canvas.draw()


class UpdatePanelTask(utils.Task):
    def __init__(self, ui:Ui_MainWindow, panel:SoundDisplayPanel):
        super(UpdatePanelTask, self).__init__()
        self.ui = ui
        self.panel = panel

    def acquire(self):
        self.ui.inputs_box.setEnabled(False)
        self.ui.outputs_box.setEnabled(False)
        self.ui.convert_btn.setEnabled(False)
        self.panel.setEnabled(False)
        return utils.ReturnCode.S_OK

    def release(self):
        self.ui.inputs_box.setEnabled(True)
        self.ui.outputs_box.setEnabled(True)
        self.ui.convert_btn.setEnabled(True)
        self.panel.setEnabled(True)
        return utils.ReturnCode.S_OK

    def functional(self, **kwargs):
        self.update_status(utils.Status.Media.RECOMPUTING)
        try:
            self.panel.show()
        except Exception as e:
            self.last_error = e
            self.status_watcher.events.error_event.emit(str(e))
            return utils.ReturnCode.FAILED
        return utils.ReturnCode.S_OK
