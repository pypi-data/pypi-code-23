import socket

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', 43435))
    print('Bound to 0.0.0.0:43435')
    while True:
        data, (ip, port) = s.recvfrom(1618)
        print('Received:', list(data))