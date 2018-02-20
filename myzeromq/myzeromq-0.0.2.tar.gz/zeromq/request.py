import google.protobuf.json_format
import test_pb2
import json
import zmq
import sys

def __init__(self):
    jsonData = json.dumps({ "id":"John", "timestamp":"90", "lang":"50" })
    message = test_pb2.test()
    print("message:",message)
    protobuf_message = google.protobuf.json_format.Parse(jsonData,message, ignore_unknown_fields=False)
    print("protobuf_message:",protobuf_message)
    #test_ob=test_pb2.test()
    #print(test_ob.SerializeToString())

#port = "1234"
def Send_Request(port):
    jsonData = json.dumps({ "id":"John", "timestamp":"90", "lang":"80" })
    message = test_pb2.test()
    print("message:",message)
    protobuf_message = google.protobuf.json_format.Parse(jsonData,message, ignore_unknown_fields=False)
    print("protobuf_message:",protobuf_message)
    context = zmq.Context()
    print ("Connecting to server...")
    socket = context.socket(zmq.REQ)
    socket.connect ("tcp://localhost:%s" % port)

    for i in range(1):
        print ("Sending request {}".format(protobuf_message))
        socket.send_pyobj(protobuf_message)
            #  Get the reply.
        message = socket.recv_pyobj()
        print ("Received reply ", "[", message,"]")       
    return  ("Received reply ", "[", message,"]") 

