from widgets.configure_form import Ui_Form
from widgets.media import RecordDisplayPanel
import libs.utils as utils

import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import QWidget, QComboBox
from PyQt5 import QtCore, QtGui

class ConfigurationForm(QWidget):
    def __init__(self, env:utils.Environment, exit_callback):
        super(ConfigurationForm, self).__init__()
        self.env                    = env
        self.exit_signal            = False
        self.interrupted_signal      = False
        self.__exit_callback__      = exit_callback
        self.widget_timer           = QtCore.QTimer(self)
        self.form                   = Ui_Form()
        self.form.setupUi(self)
        self.form.retranslateUi(self)
        self.setup_mic_test_panel()

        self.setup_combobox(
            self.form.spectrum_nfft_cobox,
            ['512', '1024', '2048', '4096'],
            int,
            [
                self.env.upper_panel_config.spectrum_config.nfft,
                self.env.lower_panel_config.spectrum_config.nfft
            ]
        )

        self.setup_combobox(
            self.form.stft_nfft_cobox,
            ['128', '256', '512', '1024', '2048'],
            int,
            [
                self.env.upper_panel_config.spectrogram_config.nfft,
                self.env.lower_panel_config.spectrogram_config.nfft
            ]
        )

        self.setup_combobox(
            self.form.stft_wtype_cobox,
            [
                'Hanning',
                'Triangle'
            ],
            str,
            [
                self.env.upper_panel_config.spectrogram_config.window_type,
                self.env.lower_panel_config.spectrogram_config.window_type
            ],
            alternative_values={
                'Hanning'   :utils.WindowType.HANN,
                'Triangle'  :utils.WindowType.TRIANGLE
            }
        )

        self.setup_combobox(
            self.form.stft_hlength_cobox,
            ['128', '256', '512'],
            int,
            [
                self.env.upper_panel_config.spectrogram_config.hop_length,
                self.env.lower_panel_config.spectrogram_config.hop_length
            ]
        )

        self.setup_combobox(
            self.form.stft_wlength_cobox,
            ['128', '256', '512', '1024', '2048'],
            int,
            [
                self.env.upper_panel_config.spectrogram_config.win_length,
                self.env.lower_panel_config.spectrogram_config.win_length
            ]
        )

        def __toggle_interrupt__():
            self.interrupted_signal = True
        qt_devices = utils.unique_filter(utils.query_qt_input_devices())
        self.setup_combobox(
            self.form.mic_devices_cobox,
            qt_devices,
            int,
            [
                self.env.mic
            ],
            alternative_values=utils.get_input_devices(qt_devices),
            callback=__toggle_interrupt__
        )

        def __log_stft_toggled__():
            self.env.upper_panel_config.spectrogram_config.abs2db.set(self.form.log_stft_cbox.isChecked())
            self.env.lower_panel_config.spectrogram_config.abs2db.set(self.form.log_stft_cbox.isChecked())
        self.form.log_stft_cbox.toggled.connect(__log_stft_toggled__)

        assert (self.env.upper_panel_config.spectrogram_config.abs2db.get() == self.env.lower_panel_config.spectrogram_config.abs2db.get())
        self.form.log_stft_cbox.setChecked(self.env.upper_panel_config.spectrogram_config.abs2db.get())

        self.widget_timer.setInterval(400)
        self.widget_timer.timeout.connect(self.form.testmic.show)
        self.widget_timer.start()

    def setup_mic_test_panel(self):
        self.form.testmic = RecordDisplayPanel(self.env.mic_test_cache, parent=self.form.mic_group)
        self.form.testmic.setGeometry(QtCore.QRect(10, 40, 271, 131))
        self.form.testmic.setObjectName("testmic")

    # set all variable in variable list to value in values
    @staticmethod
    def setup_combobox(combobox:QComboBox, values:list, val_type, target_variables:list, alternative_values=None, callback=None):
        def create_callback(variables, val_list, val_dict=None):
            def __callback__(index):
                for variable in variables:
                    if val_dict is None:
                        value = val_list[index]
                    else:
                        value = val_dict[val_list[index]]
                    variable.set(val_type(value))
                if callback is not None:
                    callback()
            return __callback__

        combobox.addItems(values)
        combobox.currentIndexChanged.connect(create_callback(target_variables, values, alternative_values))
        if alternative_values is None:
            combobox.setCurrentText(str(target_variables[0].get()))
            combobox.setCurrentIndex(values.index(str(target_variables[0].get())))
        else:
            vals = {v:k for k, v in alternative_values.items()}
            combobox.setCurrentText(str(vals[target_variables[0].get()]))
            combobox.setCurrentIndex(values.index(str(vals[target_variables[0].get()])))


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.interrupted_signal     = True
        self.exit_signal            = True
        self.widget_timer.stop()
        self.__exit_callback__()
        self.close()

class ConfigurationTask(utils.Task):
    def __init__(self, form:ConfigurationForm):
        super(ConfigurationTask, self).__init__()
        self.form = form

    def __callback__(self, indata, frames, _time, status):
        self.form.env.mic_test_cache.set(indata.reshape(-1))

    def acquire(self):
        pass

    def release(self):
        pass

    def functional(self, **kwargs):
        try:
            self.update_status(utils.Status.Configuration.CONFIG)
            while not self.form.exit_signal:
                stream = sd.InputStream(
                    device=self.form.env.mic.get(),
                    channels=1,
                    samplerate=utils.Environment.SAMPLE_RATE,
                    latency='low',
                    callback=self.__callback__
                )

                with stream:
                    while not self.form.interrupted_signal:
                        QtCore.QThread.usleep(utils.Environment.WAITING_RECORD_INTERVAL * 1000)
                    self.form.interrupted_signal = False

        except Exception as e:
            self.last_error = e
            self.status_watcher.events.error_event.emit(str(e))
            return utils.ReturnCode.FAILED
        return utils.ReturnCode.S_OK


class Configuration:
    def __init__(self, env:utils.Environment):
        self.form   = None
        self.env    = env

    def create_configuration_task(self, callback):
        self.form = ConfigurationForm(self.env, callback)
        self.form.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.form.show()
        return ConfigurationTask(self.form)