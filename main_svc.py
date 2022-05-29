from widgets.svccontrol_windows import Ui_SvcControl
from libs.services import ServiceControl
import libs.utils as utils

import sys
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QPushButton
from PyQt5 import QtCore, QtWidgets, QtGui

def show_error(info):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(info)
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def show_info(info):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(info)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

class RedPushButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, use_border=True, bg_change=True, circular=False):
        super(RedPushButton, self).__init__(parent)
        self.text_color = QtGui.QColor(255, 0, 0)
        self.bg_color = QtGui.QColor(255, 255, 255)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QtCore.Qt.GlobalColor.white)
        self.shadow.setOffset(0, 0)

        self.bg_change = bg_change
        self.circular_mode = circular

        style = 'background-color: %s; color: %s;'
        if use_border:
            style += 'border: 1px solid rgb(255, 0, 0);'

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
        self.text_animation.setStartValue(QtGui.QColor(255, 0, 0))
        self.text_animation.setEndValue(QtGui.QColor(255, 255, 255))
        self.text_animation.valueChanged.connect(self.update_text_color)

        self.bg_animation = QtCore.QVariantAnimation(self)
        self.bg_animation.setDuration(400)
        self.bg_animation.setStartValue(QtGui.QColor(255, 255, 255))
        self.bg_animation.setEndValue(QtGui.QColor(255, 0, 0))
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

class GreenPushButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, use_border=True, bg_change=True, circular=False):
        super(GreenPushButton, self).__init__(parent)
        self.text_color = QtGui.QColor(20, 227, 20)
        self.bg_color = QtGui.QColor(255, 255, 255)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QtCore.Qt.GlobalColor.white)
        self.shadow.setOffset(0, 0)

        self.bg_change = bg_change
        self.circular_mode = circular

        style = 'background-color: %s; color: %s;'
        if use_border:
            style += 'border: 1px solid rgb(20, 227, 20);'

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
        self.text_animation.setStartValue(QtGui.QColor(20, 227, 20))
        self.text_animation.setEndValue(QtGui.QColor(255, 255, 255))
        self.text_animation.valueChanged.connect(self.update_text_color)

        self.bg_animation = QtCore.QVariantAnimation(self)
        self.bg_animation.setDuration(400)
        self.bg_animation.setStartValue(QtGui.QColor(255, 255, 255))
        self.bg_animation.setEndValue(QtGui.QColor(20, 227, 20))
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

class SvcControl(QMainWindow):
    def __init__(self):
        super(SvcControl, self).__init__()
        self.ui = Ui_SvcControl()
        self.ui.setupUi(self)
        self.create_buttons()
        self.ui.retranslateUi(self)

        self.service_controller = ServiceControl(utils.ServiceType.MICROPHONE)

        self.ui.start_svc_btn.clicked.connect(self.start_service)
        self.ui.stop_svc_btn.clicked.connect(self.stop_service)


        def __update_svc_status_ui__():
            svc_stat = self.service_controller.status()
            if svc_stat is not None:
                if svc_stat == utils.ServiceState.SERVICE_RUNNING:
                    self.ui.start_svc_btn.setVisible(False)
                    self.ui.stop_svc_btn.setVisible(True)
                elif svc_stat == utils.ServiceState.SERVICE_STOPPED:
                    self.ui.start_svc_btn.setVisible(True)
                    self.ui.stop_svc_btn.setVisible(False)
        self.svc_status_timer = QtCore.QTimer()
        self.svc_status_timer.timeout.connect(__update_svc_status_ui__)

        status = self.service_controller.status()
        if status is None:
            show_error(self.service_controller.last_error)
            sys.exit(0)
        else:
            if status == utils.ServiceState.SERVICE_RUNNING:
                self.ui.start_svc_btn.setVisible(False)
            elif status == utils.ServiceState.SERVICE_STOPPED:
                self.ui.stop_svc_btn.setVisible(False)
            else:
                show_error('Service is neither running or stopped')

            self.svc_status_timer.start(200)

    def create_buttons(self):
        self.ui.stop_svc_btn = RedPushButton(self.ui.centralwidget)
        self.ui.stop_svc_btn.setGeometry(QtCore.QRect(20, 50, 141, 23))
        self.ui.stop_svc_btn.setObjectName("stop_svc_btn")

        self.ui.start_svc_btn = GreenPushButton(self.ui.centralwidget)
        self.ui.start_svc_btn.setGeometry(QtCore.QRect(20, 10, 141, 23))
        self.ui.start_svc_btn.setObjectName("start_svc_btn")

        self.ui.stop_svc_btn.setText('Stop Service')
        self.ui.start_svc_btn.setText('Start Service')



    def start_service(self):
        code = self.service_controller.start()
        if code != utils.ReturnCode.S_OK:
            show_error(self.service_controller.last_error)
            return
        else:
            show_info('Service has started')

    def stop_service(self):
        code = self.service_controller.stop()
        if code != utils.ReturnCode.S_OK:
            show_error(self.service_controller.last_error)
            return
        else:
            show_info('Service has stopped')

app = QApplication([])
if not utils.is_admin():
    show_error('Service control requires admin privileges')
    sys.exit(1)

windows = SvcControl()
windows.show()
app.exec_()

