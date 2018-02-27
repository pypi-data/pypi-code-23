import logging

from deepspeech.model import Model
import scipy.io.wavfile as wav

from jeeves import plugin


class DeepSpeechSTT(plugin.STTPlugin):
    """
    DeepSpeech Speech-to-Text implementation
    """

    def __init__(self, *args, **kwargs):
        plugin.STTPlugin.__init__(self, *args, **kwargs)
        self._logger = logging.getLogger(__name__)
        self._plugin_config = self.profile['deepspeech']
        graph = self._plugin_config['graph']
        alphabet = self._plugin_config['alphabet']
        self._logger.debug("Initializing DeepSpeech with graph '%s' " +
                           "and alphabet '%s'", graph, alphabet)
        self._model = Model(graph, 26, 9, alphabet, 500)

    def transcribe(self, fp):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
            fp -- a file object containing audio data
        """

        fs, audio = wav.read(fp)
        return self._model.stt(audio, fs)
