import subprocess
from sys import platform

import arff

from orangecontrib.audio.helper_scripts.htkmfc import *
from orangecontrib.audio.helper_scripts.audioFeatureExtraction import *
from orangecontrib.audio.helper_scripts.audioTrainTest import *


class FeatureExtraction:
    def __init__(self):
        self.DETACHED_PROCESS = 8

    def extract_emobase_features(self, file_name):
        """
        Extract emotions feature

        :param file_name: name of file
        :return: array with extracted features
        """

        output_path = os.path.dirname(file_name) + "/rezultati.arff"

        dir_path = os.path.dirname(os.path.realpath(__file__))

        config_path = dir_path + "/feature_extraction/config/emobase2010.conf"

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            smile_path = dir_path + "/feature_extraction/Linux/SMILExtract"
            subprocess.check_output([smile_path, "-C", config_path,
                                     "-I", file_name, "-O", output_path])
        else:
            smile_path = dir_path + "/feature_extraction/Win32/SMILExtract_Release"
            subprocess.check_output([smile_path, "-C", config_path, "-I", file_name,
                                     "-O", output_path], creationflags=self.DETACHED_PROCESS)

        output_data = arff.load(open(output_path, 'r'))
        os.remove(output_path)

        zipped = zip(output_data["attributes"][1:], output_data["data"][0][1:])

        array = []
        y = 1
        for i in zipped:
            array.append(i[1])
            y += 1

        return array

    def extract_mfcc_plp_features(self, file_name, id):
        """
        Extract mfcc or plp features

        :param file_name: name of file
        :param id: id of selected feature configuration
        :return: array with extracted features
        """

        output_path = os.path.dirname(file_name) + "/rezultati.htk"

        dir_path = os.path.dirname(os.path.realpath(__file__))

        if id == 2:
            config_path = dir_path + "/feature_extraction/config/MFCC12_E_D_A.conf"
        else:
            config_path = dir_path + "/feature_extraction/config/PLP_E_D_A.conf"

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            smile_path = dir_path + "/feature_extraction/Linux/SMILExtract"
            subprocess.check_output([smile_path, "-C", config_path, "-I",
                                     file_name, "-O", output_path])
        else:
            smile_path = dir_path + "/feature_extraction/Win32/SMILExtract_Release"
            subprocess.check_output([smile_path, "-C", config_path, "-I", file_name,
                                     "-O", output_path], creationflags=self.DETACHED_PROCESS)

        output_data = open_htk(output_path)
        array = list(numpy.mean(output_data.getall(), axis=0))

        return array

    def extract_chroma_features(self, file_name):
        """
        Extract chroma features

        :param file_name: name of file
        :return: array with extracted features
        """

        output_path = os.path.dirname(file_name) + "/rezultati.csv"

        dir_path = os.path.dirname(os.path.realpath(__file__))

        config_path = dir_path + "/feature_extraction/config/chroma_fft.conf"

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            smile_path = dir_path + "/feature_extraction/Linux/SMILExtract"
            subprocess.check_output([smile_path, "-C", config_path, "-I",
                                     file_name, "-O", output_path])
        else:
            smile_path = dir_path + "/feature_extraction/Win32/SMILExtract_Release"
            subprocess.check_output([smile_path, "-C", config_path, "-I",
                                     file_name, "-O", output_path], creationflags=self.DETACHED_PROCESS)

        with open(output_path, "rb") as f:
            output_data = []
            for i in f.readlines():
                output_data.append(list(numpy.fromstring(i.decode("utf-8"), dtype=float, sep=';')))

        os.remove(output_path)
        array = list(numpy.mean(numpy.array(output_data), axis=0))

        return array

    def extract_all_mean_features(self, input_data, framerate):
        """
        Extract all feature supported by the pyAudioAnalysis library

        :param input_data: raw data
        :param framerate: framerate
        :return: array with extracted features
        """

        return list(numpy.mean(stFeatureExtraction(input_data, framerate, 0.050 * framerate, 0.025 * framerate).T, axis=0))
