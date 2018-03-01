import unittest
import sys
sys.path.append("../MqttImageUploader")
import json

import MqttImageUploader as miu

url = "127.0.0.1"

def publish_callback(client, userdata, result):
    print("published data motherfuckers")
    print(result)

class MqttImageUploaderTest(unittest.TestCase):

    def testPublish(self):

        uploader = miu.MqttImageUploader(
            url, 1883, "test/test")
        uploader.UploadData(
            "./image.jpg", '{"timestamp":123123123}', publish_callback)



    def testWithDictionryJson(self):
        uploader = miu.MqttImageUploader(url, 1883, "test/test")
        j = dict()
        j['timestamp'] = 123123123
        uploader.UploadData('./image.jpg', json.dumps(j), publish_callback)

 

if __name__ == '__main__':
    unittest.main()
