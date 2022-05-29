import tensorflow as tf
import numpy as np
import librosa
import libs.utils as utils
from widgets.main_windows import Ui_MainWindow

from nara_wpe.wpe import wpe
from nara_wpe.utils import stft, istft


class Pipeline:
    MODEL_PATH = "./model"

    def __init__(self):
        self.norm_in = True
        self.norm_out = True
        self.__model = tf.saved_model.load(self.MODEL_PATH)

    def model(self, x):
        infer = self.__model.signatures["serving_default"]
        re = infer(tf.constant(x, dtype=tf.float32))
        re = re[list(re.keys())[0]]
        return np.array(re)

    def preprocess(self, x, **kwargs):
        x = librosa.util.normalize(x) if self.norm_in else np.array(x)
        return x.reshape(1, -1)

    def postprocess(self, x, **kwargs):
        x = self.__wpe__(x)
        return librosa.util.normalize(x) if self.norm_out else np.array(x)

    def __wpe__(self, x):
        X = stft(x, size=512, shift=128)
        Z = wpe(X.transpose(2, 0, 1)).transpose(1, 2, 0)
        return istft(Z, size=512, shift=128)[0]


class NoiseSuppressionTask(utils.Task):
    def __init__(self, pipeline:Pipeline, ui:Ui_MainWindow, env:utils.Environment):
        super(NoiseSuppressionTask, self).__init__()
        self.pipeline = pipeline
        self.ui = ui
        self.env = env

        self.x = None

    def acquire(self):
        self.ui.actions_box.setEnabled(False)
        self.x = self.env.input_data.get().copy()
        return utils.ReturnCode.S_OK

    def release(self):
        self.ui.actions_box.setEnabled(True)
        return utils.ReturnCode.S_OK

    def functional(self, **kwargs):
        try:
            self.pipeline.norm_in       = self.env.pipeline_config.norm_in.get()
            self.pipeline.norm_out      = self.env.pipeline_config.norm_out.get()

            self.x                      = self.pipeline.preprocess(self.x)
            self.x                      = self.pipeline.model(self.x)
            self.x                      = self.pipeline.postprocess(self.x)
            self.env.output_data.set(self.x)
        except Exception as e:
            self.last_error = e
            self.status_watcher.events.error_event.emit(str(e))
            return utils.ReturnCode.FAILED
        return utils.ReturnCode.S_OK

    def callback(self):
        self.ui.converted_sound.show()