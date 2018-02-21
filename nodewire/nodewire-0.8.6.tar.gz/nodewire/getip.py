from netifaces import AF_INET, AF_INET6, AF_LINK
import netifaces as ni
##
## http://stackoverflow.com/questions/6243276/how-to-get-the-physical-interface-ip-address-from-an-interface
##
def interfaces():
    return ni.interfaces()

def ipaddress(interface):
    if AF_INET in ni.ifaddresses(interface):
        return  ni.ifaddresses(interface)[AF_INET][0]['addr']
    else:
        return None

def connectedip():
    localaddress = None
    ifs = interfaces()
    for i in ifs:
        address = ipaddress(i)
        if address:
            if address != '127.0.0.1' and not address.startswith('169'):
                return address
            else:
                if not localaddress or localaddress=='127.0.0.1':
                    localaddress = address
    return localaddress