import time
import heapq
import sounddevice as sd
import ctypes, os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from functools import *

def unique_filter(x):
    return list(dict.fromkeys(x))

def query_qt_input_devices():
    devices = QtMultimedia.QAudioDeviceInfo.availableDevices(QtMultimedia.QAudio.Mode.AudioInput)
    return list(map(lambda x: x.deviceName(), devices))

def get_device_api(request_device, backends):
    re = None

    device_indices = list(reduce(lambda x, y: x + ([y[0]] if y[1]['name'] == request_device else []), enumerate(sd.query_devices()), []))
    for backend in backends:
        for device_idx in device_indices:
            if device_idx in backend['devices'] and sd.query_devices()[device_idx]['max_input_channels'] > 0:
                re = device_idx
                break

    return re

def get_input_devices(unique_qt_devices, request_apis=None):
    #sd_devices = sd.query_devices()
    #re = {}
    #for qt_device in unique_qt_devices:
    #    for sd_device in sd_devices:
    #        if sd_device['name'] in qt_device and qt_device not in re.keys():
    #            re[qt_device] = sd_device['name']
    if request_apis is None:
        request_apis = ['MME']

    mapping = {}
    backends = []
    host_apis = sd.query_hostapis()

    for backend in host_apis:
        if backend['name'] in request_apis:
            backends.append(backend)

    for device in unique_qt_devices:
        mapping[device] = get_device_api(device, backends)

    return mapping

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

class Task:
    def __init__(self, **functional_kwargs):
        self.kwargs = functional_kwargs

        self.timestamp = - time.time() # act as key in status watcher max heap
        self.status = Status.INIT
        self.status_watcher = None
        self.thread = None
        self.last_error = None

    def __eq__(self, other):
        return self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __le__(self, other):
        return self.timestamp <= other.timestamp

    def __gt__(self, other):
        return self.timestamp > other.timestamp

    def __ge__(self, other):
        return self.timestamp >= other.timestamp

    def update_status(self, new_status):
        self.status = new_status
        self.status_watcher.update_task_status(self)

    def acquire(self):
        raise Exception('Not implemented')

    def functional(self, **kwargs):
        raise Exception('Not implemented')

    def release(self):
        raise Exception('Not implemented')

    def callback(self):
        pass

class MaxHeap:
    def __init__(self):
        self.queue = []

    def __len__(self):
        return len(self.queue)

    def __getitem__(self, item):
        return self.queue[item]

    def put(self, x:Task):
        heapq.heappush(self.queue, x)

    def pop(self, task:Task=None):
        if task is None:
            return heapq.heappop(self.queue)
        else:
            self.queue.remove(task)
            heapq.heapify(self.queue)

    def clear(self):
        self.queue.clear()


class Events(QObject):
    error_event = pyqtSignal(str, name='error_event')
    warning_event = pyqtSignal(str, name='warning_event')
    info_event = pyqtSignal(str, name='info_event')

    def __init__(self):
        super(Events, self).__init__()


class Variable:
    def __init__(self):
        self.data = None

    def set(self, x):
        self.data = x

    def get(self):
        return self.data

class Config:
    class SpectrumConfig:
        def __init__(self):
            self.nfft = Variable()
            self.nfft.set(2048)

    class SpectrogramConfig:
        def __init__(self):
            self.nfft           = Variable()
            self.window_type    = Variable()
            self.hop_length     = Variable()
            self.win_length     = Variable()
            self.abs2db         = Variable()

            self.nfft.set(512)
            self.window_type.set(WindowType.HANN)
            self.hop_length.set(128)
            self.win_length.set(512)
            self.abs2db.set(True)

    class DisplayConfig:
        def __init__(self, data_src:Variable):
            self.spectrum_config        = Config.SpectrumConfig()
            self.spectrogram_config     = Config.SpectrogramConfig()
            self.view_mode              = Variable()
            self.data_src               = data_src

            self.view_mode.set(ViewMode.WAVEFORM)

    class PipelineConfig:
        def __init__(self):
            self.norm_in                = Variable()
            self.norm_out               = Variable()

            self.norm_in.set(True)
            self.norm_out.set(True)


class Environment:
    MIC_SERVICE_NAME        = "MicDriverService"
    SPEAKER_SERVICE_NAME    = "SpeakerDriverService"
    STATUS_FORMAT           = 'Status: {}'
    SAMPLE_RATE             = 16000
    WAITING_RECORD_INTERVAL = 400 # in milliseconds


    def __init__(self):
        self.input_data             = Variable()
        self.output_data            = Variable()
        self.record_cache           = Variable()
        self.mic                    = Variable()
        self.mic_test_cache         = Variable()
        self.service_disabled       = Variable()
        self.service_use_pipeline   = Variable()

        self.upper_panel_config     = Config.DisplayConfig(self.input_data)
        self.lower_panel_config     = Config.DisplayConfig(self.output_data)
        self.pipeline_config        = Config.PipelineConfig()

        init_mic = unique_filter(query_qt_input_devices())[0]
        self.mic.set(list(get_input_devices([init_mic]).values())[0])
        self.service_use_pipeline.set(True)
        self.service_disabled.set(False)


class PushButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, use_border=True, bg_change=True, circular=False):
        super(PushButton, self).__init__(parent)
        self.text_color = QtGui.QColor(0, 98, 255)
        self.bg_color = QtGui.QColor(255, 255, 255)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QtCore.Qt.GlobalColor.white)
        self.shadow.setOffset(0, 0)

        self.bg_change = bg_change
        self.circular_mode = circular

        style = 'background-color: %s; color: %s;'
        if use_border:
            style += 'border: 1px solid rgb(0, 98, 255);'

        if circular:
            style += 'border-radius: %s;'

        self.style_sheet_template = \
            """
                QPushButton {
                    %s
                }
            """ % style

        self.text_animation = QtCore.QVariantAnimation(self)
        self.text_animation.setDuration(400)
        self.text_animation.setStartValue(QtGui.QColor(0, 98, 255))
        self.text_animation.setEndValue(QtGui.QColor(255, 255, 255))
        self.text_animation.valueChanged.connect(self.update_text_color)

        self.bg_animation = QtCore.QVariantAnimation(self)
        self.bg_animation.setDuration(400)
        self.bg_animation.setStartValue(QtGui.QColor(255, 255, 255))
        self.bg_animation.setEndValue(QtGui.QColor(0, 98, 255))
        self.bg_animation.valueChanged.connect(self.update_bg_color)

        self.glow_animation = QtCore.QPropertyAnimation(self.shadow, b'color')
        self.glow_animation.setDuration(400)
        self.glow_animation.setStartValue(QtGui.QColor(255, 255, 255))
        self.glow_animation.setEndValue(QtGui.QColor(0, 0, 0))

        self.setGraphicsEffect(self.shadow)
        self.update_style_sheet()

    def update_text_color(self, new_color):
        self.text_color.setNamedColor(new_color.name())
        self.update_style_sheet()

    def update_bg_color(self, new_color):
        self.bg_color.setNamedColor(new_color.name())
        self.update_style_sheet()

    def update_style_sheet(self):
        self.setStyleSheet(
            self.style_sheet_template % (
                (
                    self.bg_color.name(),
                    self.text_color.name()
                )
                if not self.circular_mode else
                (
                    self.bg_color.name(),
                    self.text_color.name(),
                    self.size().height() / 2
                )
            )
        )

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.text_animation.setDirection(QtCore.QAbstractAnimation.Direction.Forward)
        self.bg_animation.setDirection(QtCore.QAbstractAnimation.Direction.Forward)
        self.glow_animation.setDirection(QtCore.QAbstractAnimation.Direction.Forward)
        self.text_animation.start()
        self.glow_animation.start()
        if self.bg_change:
            self.bg_animation.start()
        super().enterEvent(a0)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        self.text_animation.setDirection(QtCore.QAbstractAnimation.Direction.Backward)
        self.bg_animation.setDirection(QtCore.QAbstractAnimation.Direction.Backward)
        self.glow_animation.setDirection(QtCore.QAbstractAnimation.Direction.Backward)
        self.text_animation.start()
        self.glow_animation.start()
        if self.bg_change:
            self.bg_animation.start()
        super().leaveEvent(a0)




class ViewMode:
    WAVEFORM    = 'Waveform'
    SPECTRUM    = 'Spectrum'
    SPECTROGRAM = 'Spectrogram'

class ServiceType:
    MICROPHONE  = 0
    SPEAKER     = 1

class ServiceCommand:
    SERVICE_CONTROL_STOP            = 0x01
    SERVICE_CONTROL_SWITCH_NOFILTER = 0xFF
    SERVICE_CONTROL_SWITCH_PIPELINE = 0xFE

class WindowType:
    HANN            = 'hann'
    TRIANGLE        = 'triang'

class ReturnCode: # mimic HRESULT
    S_OK    = 0
    FAILED  = 1

class Status:
    INIT            = 'Initializing'
    READY           = 'Ready'
    ACQUIRE         = 'Acquiring'
    RELEASE         = 'Releasing'
    PROCESSING      = 'Processing'
    TERMINATE       = 'Terminating'
    EXIT            = 'Exit'

    class Inputs:
        LOADING     = 'Loading'
        RECORDING   = 'Recording'

    class Outputs:
        SAVING      = 'Saving'

    class Media:
        RECOMPUTING = 'Recomputing'

    class Configuration:
        CONFIG      = 'Configuring'

class ServiceState:
    SERVICE_CONTINUE_PENDING    = 0x00000005
    SERVICE_PAUSE_PENDING       = 0x00000006
    SERVICE_PAUSED              = 0x00000007
    SERVICE_RUNNING             = 0x00000004
    SERVICE_START_PENDING       = 0x00000002
    SERVICE_STOP_PENDING        = 0x00000003
    SERVICE_STOPPED             = 0x00000001
