import zmq
import time
import sys
import google.protobuf.json_format
#port = "1234"

def Send_Response(port):
    ontext = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
 

    while True:
        #  Wait for next request from client
        protobuf_message = socket.recv_pyobj()
        print ("Received request: {}".format(protobuf_message))
        #  Covert message to json
        json_string = google.protobuf.json_format.MessageToJson(protobuf_message)
        #  Try to change the protobuf_message value
        protobuf_message.id='Stanly'
        socket.send_pyobj(protobuf_message)
        #time.sleep (1)  
    return True