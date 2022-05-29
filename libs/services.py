import time

import win32service as win32
import libs.utils as utils

class ServiceInfo:
    def __init__(self, service_type):
        assert (service_type in [utils.ServiceType.SPEAKER, utils.ServiceType.MICROPHONE],
                f"Service type is not supported ({service_type})")
        if service_type == utils.ServiceType.MICROPHONE:
            self.name = utils.Environment.MIC_SERVICE_NAME
        else:
            raise "Driver is not supported"

class ServiceControl:
    def __init__(self, service_type):
        self.service_info = ServiceInfo(service_type)
        self.last_error = ''

    def status(self):
        scHandler = None
        service = None

        try:
            scHandler = win32.OpenSCManager(None, None, win32.SC_MANAGER_CONNECT)
            service = win32.OpenService(scHandler, self.service_info.name, win32.SERVICE_QUERY_STATUS)
        except Exception as e:
            self.last_error = str(e)
            if scHandler is not None:
                win32.CloseServiceHandle(scHandler)
            if service is not None:
                win32.CloseServiceHandle(service)

            return None
        status = win32.QueryServiceStatusEx(service)
        return status['CurrentState']

    def start(self):
        scHandler = None
        service = None

        try:
            scHandler = win32.OpenSCManager(None, None, win32.SC_MANAGER_ALL_ACCESS)
            service = win32.OpenService(scHandler, self.service_info.name, win32.SERVICE_ALL_ACCESS)
        except Exception as e:
            self.last_error = str(e)
            if scHandler is not None:
                win32.CloseServiceHandle(scHandler)
            if service is not None:
                win32.CloseServiceHandle(service)

            return utils.ReturnCode.FAILED

        if self.status() not in [utils.ServiceState.SERVICE_STOP_PENDING, utils.ServiceState.SERVICE_STOPPED]:
            return utils.ReturnCode.S_OK

        while self.status() == utils.ServiceState.SERVICE_STOP_PENDING:
            time.sleep(0.5)

        if self.status() != utils.ServiceState.SERVICE_STOPPED:
            print('1')
            return utils.ReturnCode.FAILED
        win32.StartService(service, [])

        while self.status() == utils.ServiceState.SERVICE_START_PENDING:
            time.sleep(0.5)

        if self.status() == utils.ServiceState.SERVICE_RUNNING:
            return utils.ReturnCode.S_OK
        else:
            return utils.ReturnCode.FAILED

    def stop(self):
        scHandler = None
        service = None

        try:
            scHandler = win32.OpenSCManager(None, None, win32.SC_MANAGER_CONNECT)
            service = win32.OpenService(scHandler, self.service_info.name, win32.SERVICE_STOP)
        except Exception as e:
            self.last_error = str(e)
            if scHandler is not None:
                win32.CloseServiceHandle(scHandler)
            if service is not None:
                win32.CloseServiceHandle(service)

            return utils.ReturnCode.FAILED

        if self.status() in [utils.ServiceState.SERVICE_STOP_PENDING, utils.ServiceState.SERVICE_STOPPED]:
            return utils.ReturnCode.S_OK

        while self.status() == utils.ServiceState.SERVICE_START_PENDING:
            time.sleep(0.5)

        if self.status() != utils.ServiceState.SERVICE_RUNNING:
            return utils.ReturnCode.FAILED
        win32.ControlService(service, utils.ServiceCommand.SERVICE_CONTROL_STOP)

        while self.status() == utils.ServiceState.SERVICE_STOP_PENDING:
            time.sleep(0.5)

        if self.status() == utils.ServiceState.SERVICE_STOPPED:
            return utils.ReturnCode.S_OK
        else:
            return utils.ReturnCode.FAILED

    def service_control(self, command):
        assert(
            command in
            [
                utils.ServiceCommand.SERVICE_CONTROL_SWITCH_NOFILTER,
                utils.ServiceCommand.SERVICE_CONTROL_SWITCH_PIPELINE
            ],
            "Not a valid command"
        )

        scHandler = None
        service = None

        try:
            scHandler   = win32.OpenSCManager(None, None, win32.SC_MANAGER_CONNECT)
            service     = win32.OpenService(scHandler, self.service_info.name, win32.SERVICE_USER_DEFINED_CONTROL)
        except Exception as e:
            self.last_error = str(e)
            if scHandler is not None:
                win32.CloseServiceHandle(scHandler)
            if service is not None:
                win32.CloseServiceHandle(service)

            return utils.ReturnCode.FAILED

        if service is not None:
            win32.ControlService(service, command)
        else:
            self.last_error = 'Service is None'
            return utils.ReturnCode.FAILED

        win32.CloseServiceHandle(scHandler)
        win32.CloseServiceHandle(service)
        return utils.ReturnCode.S_OK



