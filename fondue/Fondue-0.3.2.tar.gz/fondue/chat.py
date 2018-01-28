import sys
import select
import socket


def main():
    if len(sys.argv) == 3:
        ip, peer = sys.argv[1:]
        print('Self:', ip, 'Peer:', peer)
        peer_addr = peer, 43435
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((ip, 43435))
        s.setblocking(0)
        while True:
            send = ''
            read, write, err = select.select([sys.stdin, s], [s], [s])
            for readfrom in read:
                if readfrom == sys.stdin:
                    send += sys.stdin.readline()
                elif readfrom == s:
                    recv, sender_addr = s.recvfrom(4096)
                    if sender_addr != peer_addr:
                        break
                    print(str(recv, 'utf-8'), end='')
            for writeto in write:
                if writeto == s and len(send) > 0:
                    s.sendto(bytes(send, 'utf-8'), peer_addr)
                    send = ''


if __name__ == '__main__':
    main()