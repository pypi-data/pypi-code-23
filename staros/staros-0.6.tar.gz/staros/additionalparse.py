

def _getsubsinfoparse(info):
    e1 = info[0]
    r1 = ""
    r2 = ""
    r3 = ""
    r4 = ""
    r5 = ""
    r6 = ""

    if info[0]=="S":
        r1 = "pdsn-simple-ip"
    elif info[0]=="P":
        r1 = "ggsn-pdp-type-ppp"
    elif info[0]=="I":
        r1 = "ggsn-pdp-type-ipv4"
    elif info[0]=="V":
        r1 = "ggsn-pdp-type-ipv6"
    elif info[0]=="z":
        r1 = "ggsn-pdp-type-ipv4v6"
    elif info[0]=="R":
        r1 = "sgw-gtp-ipv4"
    elif info[0]=="W":
        r1 = "pgw-gtp-ipv4"
    elif info[0]=="B":
        r1 = "pgw-gtp-non-ip"
    elif info[0]=="@":
        r1 = "saegw-gtp-ipv4"
    elif info[0]=="&":
        r1 = "samog-ip"
    elif info[0]=="p":
        r1 = "sgsn-pdp-type-ppp"
    elif info[0]=="6":
        r1 = "sgsn-pdp-type-ipv6"
    elif info[0]=="L":
        r1 = "pdif-simple-ip"
    elif info[0]=="F":
        r1 = "standalone-fa"
    elif info[0]=="e":
        r1 = "ggsn-mbms-ue"
    elif info[0]=="E":
        r1 = "ha-mobile-ipv6"
    elif info[0]=="f":
        r1 = "hnbgw-hnb"
    elif info[0]=="X":
        r1 = "HSGW"
    elif info[0]=="m":
        r1 = "henbgw-henb"
    elif info[0]=="D":
        r1 = "bng-simple-ip"
    elif info[0]=="u":
        r1 = "Unknown"
    elif info[0]=="+":
        r1 = "samog-eogre"
    elif info[0] == "M":
        r1 = "pdsn-mobile-ip"
    elif info[0] == "h":
        r1 = "ha-ipsec"
    elif info[0] == "O":
        r1 = "sgw-gtp-ipv6"
    elif info[0] == "Y":
        r1 = "pgw-gtp-ipv6"
    elif info[0] == "J":
        r1 = "sgw-gtp-non-ip"
    elif info[0] == "#":
        r1 = "saegw-gtp-ipv6"
    elif info[0] == "^":
        r1 = "cgw-gtp-ipv6"
    elif info[0] == "s":
        r1 = "sgsn"
    elif info[0] == "2":
        r1 = "sgsn-pdp-type-ipv4-ipv6"
    elif info[0] == "K":
        r1 = "pdif-mobile-ip"
    elif info[0] == "U":
        r1 = "pdg-ipsec-ipv4"
    elif info[0] == "T":
        r1 = "pdg-ssl"
    elif info[0] == "g":
        r1 = "hnbgw-iu"
    elif info[0] == "k":
        r1 = "PCC"
    elif info[0] == "n":
        r1 = "ePDG"
    elif info[0] == "q":
        r1 = "wsg-simple-ip"
    elif info[0] == "l":
        r1 = "pgw-pmip"
    elif info[0] == "%":
        r1 = "eMBMS-ipv4"
    elif info[0] == "H":
        r1 = "ha-mobile-ip"
    elif info[0] == "N":
        r1 = "lns-l2tp"
    elif info[0] == "G":
        r1 = "IPSG"
    elif info[0] == "C":
        r1 = "cscf-sip"
    elif info[0] == "A":
        r1 = "X2GW"
    elif info[0] == "Q":
        r1 = "sgw-gtp-ipv4-ipv6"
    elif info[0] == "Z":
        r1 = "pgw-gtp-ipv4-ipv6"
    elif info[0] == "$":
        r1 = "saegw-gtp-ipv4-ipv6"
    elif info[0] == "*":
        r1 = "cgw-gtp-ipv4-ipv6"
    elif info[0] == "4":
        r1 = "sgsn-pdp-type-ip"
    elif info[0] == "o":
        r1 = "femto-ip"
    elif info[0] == "v":
        r1 = "pdg-ipsec-ipv6"
    elif info[0] == "x":
        r1 = "s1-mme"
    elif info[0] == "t":
        r1 = "henbgw-ue"
    elif info[0] == "r":
        r1 = "samog-pmip"
    elif info[0] == "3":
        r1 = "GILAN"
    elif info[0] == "!":
        r1 = "eMBMS-ipv6"



    if info[1]=="X":
        r2 = "CDMA 1xRTT"
    elif info[1]=="D":
        r2 = "CDMA EV-DO"
    elif info[1]=="A":
        r2 = "CDMA EV-DO REVA"
    elif info[1]=="C":
        r2 = "CDMA Other"
    elif info[1]=="P":
        r2 = "PDIF"
    elif info[1]=="T":
        r2 = "eUTRAN"
    elif info[1]=="N":
        r2 = "NB-IoT"
    elif info[1]=="E":
        r2 = "GPRS GERAN"
    elif info[1]=="U":
        r2 = "WCDMA UTRAN"
    elif info[1]=="G":
        r2 = "GPRS Other"
    elif info[1]=="J":
        r2 = "GAN"
    elif info[1]=="S":
        r2 = "HSPA"
    elif info[1]=="B":
        r2 = "PPPoE"
    elif info[1]=="Q":
        r2 = "WSG"
    elif info[1]=="I":
        r2 = "IP"
    elif info[1]=="W":
        r2 = "Wireless LAN"
    elif info[1]=="M":
        r2 = "WiMax"
    elif info[1]=="O":
        r2 = "Femto IPSec"
    elif info[1]=="L":
        r2 = "eHRPD"
    elif info[1]=="F":
        r2 = "FEMTO UTRAN"
    elif info[1]==".":
        r2 = "Other/Unknown"


    if info[2]=="C":
        r3 = "Connected"
    elif info[2]=="c":
        r3 = "Connecting"
    elif info[2]=="d":
        r3 = "Disconnecting"
    elif info[2]=="u":
        r3 = "Unknown"
    elif info[2]=="R":
        r3 = "CSCF-Registered"
    elif info[2]=="U":
        r3 = "CSCF-Unregistered"

    if info[3]=="A":
        r4 = "Attached"
    elif info[3]=="N":
        r4 = "Not Attached"
    elif info[3]==".":
        r4 = "Not Applicable"

    if info[4]=="A":
        r5 = "Online/Active"
    elif info[4]=="D":
        r5 = "Dormant/Idle"

    if info[5]=="I":
        r6 = "IP"
    elif info[5]=="P":
        r6 = "Proxy-Mobile-IP"
    elif info[5]=="V":
        r6 = "IPv6-in-IPv4"
    elif info[5]=="A":
        r6 = "R4 (IP-GRE)"
    elif info[5]=="W":
        r6 = "PMIPv6(IPv4)"
    elif info[5]=="v":
        r6 = "PMIPv6(IPv6)"
    elif info[5]=="N":
        r6 = "NON-IP"
    elif info[5]=="M":
        r6 = "Mobile-IP"
    elif info[5]=="i":
        r6 = "IP-in-IP"
    elif info[5]=="S":
        r6 = "IPSEC"
    elif info[5]=="T":
        r6 = "IPv6"
    elif info[5]=="Y":
        r6 = "PMIPv6(IPv4+IPv6)"
    elif info[5]=="/":
        r6 = "GTPv1(For SAMOG)"
    elif info[5]=="x":
        r6 = "UDP-IPv4"
    elif info[5] == "L":
        r6 = "L2TP"
    elif info[5] == "G":
        r6 = "GRE"
    elif info[5] == "C":
        r6 = "GTP"
    elif info[5] == "u":
        r6 = "Unknown"
    elif info[5] == "R":
        r6 = "IPv4+IPv6"
    elif info[5] == "+":
        r6 = "GTPv2(For SAMOG)"
    elif info[5] == "X":
        r6 = "UDP-IPv6"

    res = {"Access type":r1,
           "Access tech":r2,
           "Call state":r3,
           "Access CSCF status":r4,
           "Link status":r5,
           "Network type":r6}
    return res