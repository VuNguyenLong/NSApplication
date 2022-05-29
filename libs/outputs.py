from widgets.main_windows import Ui_MainWindow
from libs.fileops import FileDialog
import libs.utils as utils

import soundfile as sf

class SaveOutput(utils.Task):
    def __init__(self, filepath, ui:Ui_MainWindow, env:utils.Environment):
        super(SaveOutput, self).__init__()
        self.filepath = filepath
        self.ui = ui
        self.env = env

    def acquire(self):
        self.ui.outputs_box.setEnabled(False)
        return utils.ReturnCode.S_OK

    def release(self):
        self.ui.outputs_box.setEnabled(True)
        return utils.ReturnCode.S_OK

    def functional(self, **kwargs):
        try:
            self.update_status(utils.Status.Outputs.SAVING)
            sf.write(self.filepath, self.env.output_data.get(), self.env.SAMPLE_RATE)
        except Exception as e:
            self.last_error = e
            self.status_watcher.events.error_event.emit(str(e))
            return utils.ReturnCode.FAILED

        self.status_watcher.events.info_event.emit('Data saved')
        return utils.ReturnCode.S_OK




# handle outputs group function
class Outputs:
    def __init__(self, ui:Ui_MainWindow, file_dialog:FileDialog, env:utils.Environment):
        self.ui = ui
        self.env = env
        self.file_dialog = file_dialog

    def create_save_task(self):
        filepath = self.file_dialog.save_file(['*.wav'])
        if filepath == '':
            return None
        return SaveOutput(filepath, self.ui, self.env)