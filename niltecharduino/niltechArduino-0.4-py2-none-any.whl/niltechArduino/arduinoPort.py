
def read():
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())

    for i in range (len(ports)):
        print ports[i]
        if 'Arduino' in str(ports[i]):
            #print 'yes'
            l = str(ports[i]).split(" ")
            #print l[0]
            return l[0]
            break
        else:
            print 'Arduino Not Found'
