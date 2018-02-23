from __future__ import print_function
import uuid
import grpc
import json
import shutil
import yaml
import vaisdemo.speech.v1.cloud_speech_pb2_grpc as cloud_speech_pb2_grpc
import vaisdemo.speech.v1.cloud_speech_pb2 as cloud_speech_pb2
import threading
import importlib
import vaisdemo.capture as capture

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
    def __init__(self, api_key, resources_path=None, silence=False):
        self.api_key = api_key
        self.url = "service.grpc.vais.vn:50051"
        self.channel = grpc.insecure_channel(self.url)
        self.channel.subscribe(callback=self.connectivity_callback, try_to_connect=True)
        self.stop = False
        self.stub = cloud_speech_pb2_grpc.SpeechStub(self.channel)
        self.capture = capture.Capture({'sound': {'input_device': 0}}, "/tmp/audio")
        self.asr_callback = None

    def state_callback(*args):
        pass

    def __enter__(self):
        self.capture.setup(self.state_callback)
        return self

    def __exit__(self, *args):
        self.capture.cleanup()
        shutil.rmtree("/tmp/audio")

    def connectivity_callback(self, c):
        pass

    def get_speech(self):
        audio_stream = self.capture.silence_listener()
        for data in audio_stream:
            if encoder:
                data = encoder.encode(data)
            yield data

    def generate_messages(self):
        audio_encode = cloud_speech_pb2.RecognitionConfig.SPEEX_WITH_HEADER_BYTE
        if encoder is None:
            audio_encode = cloud_speech_pb2.RecognitionConfig.LINEAR16

        config = cloud_speech_pb2.RecognitionConfig(encoding=audio_encode)
        streaming_config = cloud_speech_pb2.StreamingRecognitionConfig(config=config, single_utterance=False, interim_results=True)
        request = cloud_speech_pb2.StreamingRecognizeRequest(streaming_config=streaming_config)
        yield request
        for audio in self.get_speech():
            request = cloud_speech_pb2.StreamingRecognizeRequest(audio_content=audio)
            yield request

    def asr(self):
        metadata = [(b'api-key', self.api_key)]
        try:
            responses = self.stub.StreamingRecognize(self.generate_messages(), metadata=metadata)
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
