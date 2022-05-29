from widgets.main_windows import Ui_MainWindow
from libs.status_watcher import StatusWatcher
from libs.multiprocessing import FunctionalThread
from libs.inputs import Inputs
from libs.outputs import Outputs
from libs.pipeline import NoiseSuppressionTask, Pipeline
from libs.fileops import FileDialog
from libs.configuration import Configuration
from libs.services import ServiceControl
import libs.utils as utils
from widgets.media import SoundDisplayPanel, UpdatePanelTask

from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QActionGroup, QAction
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5 import QtCore, QtWidgets, QtGui
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.ui                 = Ui_MainWindow()
        self.main_task          = utils.Task()
        self.events             = utils.Events()
        self.env                = utils.Environment()
        self.file_dialog        = FileDialog()
        self.pipeline           = Pipeline()

        self.ui.setupUi(self)
        self.create_panels()
        self.create_btn()
        self.create_loading_gif()
        self.ui.retranslateUi(self)

        window_icon             = QIcon(':/icons/icon')
        self.setWindowIcon(window_icon)

        self.service_controller = ServiceControl(utils.ServiceType.MICROPHONE)
        self.status_watcher     = StatusWatcher(self.ui, self.env, self.events)
        self.inputs             = Inputs(self.ui, self.file_dialog, self.env)
        self.outputs            = Outputs(self.ui, self.file_dialog, self.env)
        self.configuration      = Configuration(self.env)

        self.status_watcher.register(self.main_task)
        self.create_menu_context()

        self.ui.import_btn.clicked.connect(lambda : self.create_task_context(self.inputs.create_import_task()))
        self.ui.record_btn.clicked.connect(lambda : self.create_task_context(self.inputs.create_recording_task()))
        self.ui.export_btn.clicked.connect(lambda : self.create_task_context(self.outputs.create_save_task()))
        self.ui.convert_btn.clicked.connect(lambda : self.create_task_context(NoiseSuppressionTask(self.pipeline, self.ui, self.env)))

        def __config_exit_callback__():
            self.create_task_context(UpdatePanelTask(self.ui, self.ui.original_sound))
            self.create_task_context(UpdatePanelTask(self.ui, self.ui.converted_sound))
        self.ui.config_btn.clicked.connect(lambda : self.create_task_context(self.configuration.create_configuration_task(__config_exit_callback__)))

        self.ui.norm_in_cbox.toggled.connect(lambda : self.env.pipeline_config.norm_in.set(self.ui.norm_in_cbox.isChecked()))
        self.ui.norm_out_cbox.toggled.connect(lambda : self.env.pipeline_config.norm_out.set(self.ui.norm_out_cbox.isChecked()))
        self.main_task.update_status(utils.Status.READY)

        def __service_switch_filter__():
            self.env.service_use_pipeline.set(self.ui.mic_pipeline_cbox.isChecked())
            if not self.env.service_disabled.get():
                if self.env.service_use_pipeline.get():
                    self.service_controller.service_control(utils.ServiceCommand.SERVICE_CONTROL_SWITCH_PIPELINE)
                else:
                    self.service_controller.service_control(utils.ServiceCommand.SERVICE_CONTROL_SWITCH_NOFILTER)
        self.ui.mic_pipeline_cbox.toggled.connect(__service_switch_filter__)
        self.ui.mic_pipeline_cbox.setChecked(self.env.service_use_pipeline.get())

        def __update_svc_status_ui__():
            svc_stat = self.service_controller.status()
            if svc_stat is not None:
                if svc_stat == utils.ServiceState.SERVICE_RUNNING:
                    self.ui.mic_pipeline_cbox.setEnabled(True)
                    self.env.service_disabled.set(False)
                else:
                    self.ui.mic_pipeline_cbox.setEnabled(False)
                    self.env.service_disabled.set(True)
        self.svc_status_timer = QtCore.QTimer()
        self.svc_status_timer.timeout.connect(__update_svc_status_ui__)

        status = self.service_controller.status()
        if status is not None:
            if status != utils.ServiceState.SERVICE_RUNNING:
                self.events.warning_event.emit('Service is not running, Realtime NS will be disabled')
                self.ui.mic_pipeline_cbox.setEnabled(False)
                self.env.service_disabled.set(True)
            else:
                if self.env.service_use_pipeline.get():
                    self.service_controller.service_control(utils.ServiceCommand.SERVICE_CONTROL_SWITCH_PIPELINE)
                else:
                    self.service_controller.service_control(utils.ServiceCommand.SERVICE_CONTROL_SWITCH_NOFILTER)

            self.svc_status_timer.start(200)
        else:
            self.events.error_event.emit('Service control queries status error ' + self.service_controller.last_error + ', Realtime NS will be disabled')
            self.ui.mic_pipeline_cbox.setEnabled(False)
            self.env.service_disabled.set(True)

    def create_task_context(self, task:utils.Task):
        if task is None:
            return
        self.status_watcher.register(task)

        thread = FunctionalThread(task)
        task.thread = thread
        thread.start()

    def create_btn(self):
        self.ui.import_btn = utils.PushButton(self.ui.inputs_box)
        self.ui.import_btn.setGeometry(QtCore.QRect(40, 20, 75, 23))
        self.ui.import_btn.setObjectName("import_btn")

        self.ui.record_btn = utils.PushButton(self.ui.inputs_box)
        self.ui.record_btn.setGeometry(QtCore.QRect(40, 50, 75, 23))
        self.ui.record_btn.setObjectName("record_btn")

        self.ui.export_btn = utils.PushButton(self.ui.outputs_box)
        self.ui.export_btn.setGeometry(QtCore.QRect(40, 30, 75, 23))
        self.ui.export_btn.setObjectName("export_btn")

        self.ui.convert_btn = utils.PushButton(self.ui.actions_box, use_border=False, bg_change=False, circular=True)
        self.ui.convert_btn.setGeometry(QtCore.QRect(50, 70, 50, 50))
        self.ui.convert_btn.setToolTipDuration(-1)
        self.ui.convert_btn.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/convert"), QIcon.Normal, QIcon.Off)
        self.ui.convert_btn.setIcon(icon)
        self.ui.convert_btn.setIconSize(QtCore.QSize(50, 50))
        self.ui.convert_btn.setObjectName("convert_btn")

        self.ui.config_btn = utils.PushButton(self.ui.centralwidget, use_border=False, bg_change=False, circular=True)
        self.ui.config_btn.setGeometry(QtCore.QRect(700, 385, 30, 30))
        self.ui.config_btn.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/configure"), QIcon.Normal, QIcon.Off)
        self.ui.config_btn.setIcon(icon)
        self.ui.config_btn.setIconSize(QtCore.QSize(21, 21))
        self.ui.config_btn.setObjectName("config_btn")

        self.ui.import_btn.setText("Import")
        self.ui.record_btn.setText("Record")
        self.ui.export_btn.setText("Export")


    def create_panels(self):
        self.ui.original_sound = SoundDisplayPanel(self.env.upper_panel_config, parent=self.ui.centralwidget)
        self.ui.original_sound.setGeometry(QtCore.QRect(20, 10, 721, 181))
        self.ui.original_sound.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.ui.original_sound.setObjectName("original_sound")

        self.ui.converted_sound = SoundDisplayPanel(self.env.lower_panel_config, parent=self.ui.centralwidget)
        self.ui.converted_sound.setGeometry(QtCore.QRect(20, 200, 721, 181))
        self.ui.converted_sound.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.ui.converted_sound.setObjectName("converted_sound")


    def create_loading_gif(self):
        self.ui.status_icon = QtWidgets.QLabel(self.ui.centralwidget)
        self.ui.status_icon.setEnabled(True)
        self.ui.status_icon.setGeometry(QtCore.QRect(150, 390, 21, 21))
        self.ui.status_icon.setText("")
        self.ui.status_icon.setScaledContents(True)
        self.ui.status_icon.setObjectName("status_icon")

        self.ui.movie = QMovie(":/icons/loading")
        self.ui.status_icon.setMovie(self.ui.movie)
        self.ui.status_icon.setVisible(False)
        self.ui.movie.start()


    def create_menu_context(self):
        self.create_menu_actions(
            self.ui.original_sound,
            [
                utils.ViewMode.WAVEFORM,
                utils.ViewMode.SPECTRUM,
                utils.ViewMode.SPECTROGRAM
            ],
            self.env.upper_panel_config.view_mode,
            callback=lambda: self.create_task_context(UpdatePanelTask(self.ui, self.ui.original_sound))
        )

        self.create_menu_actions(
            self.ui.converted_sound,
            [
                utils.ViewMode.WAVEFORM,
                utils.ViewMode.SPECTRUM,
                utils.ViewMode.SPECTROGRAM
            ],
            self.env.lower_panel_config.view_mode,
            callback=lambda: self.create_task_context(UpdatePanelTask(self.ui, self.ui.converted_sound))
        )


    @staticmethod
    def create_menu_actions(menu:QMenu, values, env_target, default_val_index=0, callback=None, **callback_data):
        def create_action(v):
            def __action__():
                env_target.set(v)
                if callback is not None:
                    callback(**callback_data)
            return __action__

        action_group = QActionGroup(menu)
        for i, value in enumerate(values):
            action = QAction(str(value), parent=menu)
            action.setCheckable(True)

            func = create_action(value)
            action.triggered.connect(func)
            if i == default_val_index:
                action.setChecked(True)
                func()

            action_group.addAction(action)
            menu.addAction(action)



app = QApplication([])
windows = App()
windows.show()
app.exec_()