
def getPort():
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())

    for i in range (len(ports)):
        #print ports[i]
        if 'Arduino' in str(ports[i]):
            #print 'yes'
            l = str(ports[i]).split(" ")
            #print l[0]
            return l[0]
            break
        else:
            print 'Arduino Not Found'

def readData(startByte,stopByte,Baudrate,Timeout):
    
        import serial

        import time

        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())

        for i in range (len(ports)):
            #print ports[i]
            if 'Arduino' in str(ports[i]):
                #print 'yes'
                l = str(ports[i]).split(" ")
                #print l[0]
                x = l[0]
                break
        else:
            print 'Arduino Not Found'

        ser = serial.Serial(x, Baudrate, timeout=Timeout)
        
        inputx = ser.readline()

        input_number = (inputx.decode("utf-8"))
        i = 0
        for i in range (len(input_number)):
               if input_number[i] == startByte:
                      break

        j = 0
        for j in range (len(input_number)):
               if input_number[j] == stopByte:
                      break 
                
        f = str(input_number[i+1:j])
        
        return f



def extractData(startByte,stopByte,data):


        input_number = data
        i = 0
        for i in range (len(input_number)):
               if input_number[i] == startByte:
                      break

        j = 0
        for j in range (len(input_number)):
               if input_number[j] == stopByte:
                      break 
                
        f = str(input_number[i+1:j])
        
        return f
    



