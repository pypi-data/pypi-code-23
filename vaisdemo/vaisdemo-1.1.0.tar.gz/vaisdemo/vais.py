from __future__ import print_function
import uuid
import grpc
import json
import audioop
import shutil
import yaml
import vaisdemo.speech.v1.cloud_speech_pb2_grpc as cloud_speech_pb2_grpc
import vaisdemo.speech.v1.cloud_speech_pb2 as cloud_speech_pb2
import threading
import importlib
import vaisdemo.capture as capture
import wave

try:
    import pyaudio
except Exception as e:
    print("You don't have pyaudio installed")
    exit(1)

CHUNK = 640
encoder = None
try:
    from speex import WBEncoder
    encoder = WBEncoder()
    encoder.quality = 10
    packet_size = encoder.frame_size
    CHUNK = packet_size
except Exception as e:
    print("******** WARNING ******************************************************")
    print("* You don't have pyspeex https://github.com/NuanceDev/pyspeex installed. You might suffer from low speed performance! *")
    print("")
    print("***********************************************************************")

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 15

class VaisService():
    def __init__(self, api_key, resources_path=None, silence=False, mic_name=None):
        self.api_key = api_key
        self.url = "service.grpc.vais.vn:50051"
        self.channel = grpc.insecure_channel(self.url)
        self.channel.subscribe(callback=self.connectivity_callback, try_to_connect=True)
        self.stop = False
        self.stub = cloud_speech_pb2_grpc.SpeechStub(self.channel)
        self.volume = 0
        self.mic_name = mic_name
        self.capture = capture.Capture({'sound': {'input_device': mic_name}}, "/tmp/audio")
        self.asr_callback = None

    def state_callback(*args):
        pass

    def __enter__(self):
        self.capture.setup(self.state_callback)
        return self

    def __exit__(self, *args):
        # print("stop ASR")
        self.capture.cleanup()
        try:
            shutil.rmtree("/tmp/audio")
        except Exception as e:
            pass

    def connectivity_callback(self, c):
        pass

    def get_speech(self):
        try:
            audio_stream = self.capture.silence_listener()
            for data in audio_stream:
                self.volume = audioop.max(data, 2)
                if encoder:
                    data = encoder.encode(data)
                yield data
        except Exception as e:
            print(e)
            self.asr_callback(e.message, False)

    def load_audio(self, fname):
        fin = wave.open(fname)
        nframes = fin.getnframes()
        chunk_size = 640
        total_read = 0
        n_read = 0
        while total_read < nframes:
            n_read += 1
            nframe_left = nframes - total_read
            read_size = chunk_size
            if chunk_size > nframe_left:
                read_size = nframe_left

            data = fin.readframes(read_size)
            self.volume = audioop.max(data, 2)
            if encoder:
                data = encoder.encode(data)
            total_read += read_size
            yield data

    def generate_messages(self, filename=None):
        audio_encode = cloud_speech_pb2.RecognitionConfig.SPEEX_WITH_HEADER_BYTE
        if encoder is None:
            audio_encode = cloud_speech_pb2.RecognitionConfig.LINEAR16

        config = cloud_speech_pb2.RecognitionConfig(encoding=audio_encode)
        streaming_config = cloud_speech_pb2.StreamingRecognitionConfig(config=config, single_utterance=False, interim_results=True)
        request = cloud_speech_pb2.StreamingRecognizeRequest(streaming_config=streaming_config)
        yield request
        speech_iter = None
        if not filename:
            speech_iter = self.get_speech()
        else:
            speech_iter = self.load_audio(filename)

        self.asr_callback("Ready!", False)
        for audio in speech_iter:
            request = cloud_speech_pb2.StreamingRecognizeRequest(audio_content=audio)
            yield request

    def asr(self, filename=None):
        # print("start ASR")
        self.asr_callback("Connecting ...", False)
        metadata = [(b'api-key', self.api_key)]
        try:
            responses = self.stub.StreamingRecognize(self.generate_messages(filename=filename), metadata=metadata)
            for response in responses:
                try:
                    if response.results:
                        if response.results[0].alternatives:
                            self.asr_callback(response.results[0].alternatives[0].transcript, response.results[0].is_final)

                    # if response.is_final:
                        # if self.asr_callback:
                            # self.asr_callback(response.asr_response.results[0].alternatives[0].transcript)
                    # else:
                        # if self.asr_callback:
                            # self.asr_callback(response.asr_response.results[0].alternatives[0].transcript)
                except Exception as e:
                    print(e)
                    pass

        except grpc._channel._Rendezvous as e:
            print(e)

if __name__ == "__main__":
    def on_result(output, is_final):
        print(output, is_final)

    with VaisService("demo") as a:
        a.asr_callback = on_result
        print(a.capture._device_info.get_device_list(input_only=False))
        a.asr()
