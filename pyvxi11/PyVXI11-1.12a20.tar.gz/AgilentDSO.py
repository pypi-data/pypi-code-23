#
#-*- coding:utf-8 -*-
"""
A module to support
for Algilent DSO
(C) Noboru Yamamoto,2009. KEK, Ibaraki, JAPAN
Reference:
jkjblad04.14: vxi11scan 

 Get RPC info
   program vers proto   port
    100000    2   udp    111  portmapper
    100000    2   tcp    111  portmapper
    395180    1   tcp   1024
    395183    1   tcp   1024

link created to gpib0,7 
	 Error code:0
	 LinkID:22529568
	 port 999
	 MaxRecvSize:16384
Device is remote. RC:0
wrote *IDN?;

	 Error code:0
	 Size:7
start to read
52 bytes data read:AGILENT TECHNOLOGIES,DSO6014L,MY47090019,05.10.0284

#DSO6014A  on 2013/08/19 by NY
rpcinfo -p 169.254.254.254
   program vers proto   port
    100000    2   udp    111  portmapper
    100000    2   tcp    111  portmapper
    395180    1   tcp   1024  #???
    395183    1   tcp   1024  #VXI11_CORE 0x0607AF

% python vxi11scan.py 169.254.254.254 "gpib0,7"
link created to gpib0,7 

	 Error code:0
	 LinkID:33536912
	 port 1012
	 MaxRecvSize:16384

Device is remote. RC:0

wrote *IDN?

52 bytes data read:AGILENT TECHNOLOGIES,DSO6014A,MY48260329,05.26.0001

# DSO6014A
[noboru-mbookpro:python/VXI11/PyVXI11-Current] noboru% rpcinfo -p 192.168.2.10
   program vers proto   port
    100000    2   udp    111  portmapper
    100000    2   tcp    111  portmapper
    395180    1   tcp   1024
    395183    1   tcp   1024

% sudo /usr/local/bin/nmap -sS 192.168.2.10

Starting Nmap 6.40-2 ( http://nmap.org ) at 2013-12-17 11:34 JST
Nmap scan report for 192.168.2.10
Host is up (0.00044s latency).
Not shown: 994 closed ports
PORT     STATE SERVICE
21/tcp   open  ftp
80/tcp   open  http
111/tcp  open  rpcbind
1024/tcp open  kdm -> vxi11-core
5810/tcp open  unknown :vxWorks login(telnet)
5900/tcp open  vnc 
MAC Address: 00:30:D3:10:85:98 (Agilent Technologies)

Nmap done: 1 IP address (1 host up) scanned in 7.40 seconds

web interface also shows:
5025 for SCPI TCP/IP socket port
5024 SCPI telnet port

LXI class C/ver.1.1: Web Interface
"""

#import vxi11Device
import cVXI11
import time,types,struct,sys
if sys.version_info.major==2:
    from  exceptions import ValueError
import numpy as np
    
try:
    import numpy
    _use_numpy_fromstring=True
except:
    _use_numpy_fromstring=False

class AglDSO(cVXI11.Vxi11Device):
    def __init__(self,host, device="gpib0,7", proto="tcp"):
        cVXI11.Vxi11Device.__init__(self, host, device, proto)
        self.IDN_Str=self.qIDN()
        self.write("VERBOSE ON;")
        self.write("HEADER OFF;")
        ID=self.IDN_Str[:-1].split(",")
        self.Make=ID[0]
        self.Model=ID[1]
        self.Option=ID[3]

    def respToDict(self, lables,resp):
        v=resp[:-1].split(";")
        d={}
        d.update(list(zip(lables,v)))
        return d
    
    def qAckState(self):
        return self.ask("")

    def qAcqStopAfter(self,cmd=""):
        return self.ask("")

    def set_AcqStopAfter(self,stopafter):
        pass

    def set_AcqState(runstate):
        pass

    def qACQMODE(self):
        return self.qAcqMode()

    def qAcqMode(self):
        "<mode> ::= {RTIMe | ETIMe | SEGMented}"
        self.write("ACQ:MODE?;")
        return self.read()

    def qAcqType(self):
        self.write("ACQ:TYPE?;")
        return self.read()

    def AcqType(self,atype="HRES"):
        """
        <type> ::= {NORMal | AVERage | HRESolution | PEAK}
        """
        self.write("ACQ:TYPE %s;"%atype)

    def qBusy(self):
        return self.ask(":ACT?;")

    def qActivity(self):
        return self.ask(":ACT?;")

    def Activity(self):
        " Clears the cumulative edge variables. "
        return self.write(":ACT;")

    def qOPC(self,io_timeout=10000):
        self.write("*OPC?;")
        return self.read(io_timeout=io_timeout)

    def Run(self):
        self.write("RUN;")

    def Single(self):
        self.write("SINGLE;")

    def Stop(self):
        self.write("STOP;")

    def Status(self,disp="CHAN1"):
        """
        <display> ::= {CHANnel<n>
        |DIGital0,..,DIGital15
        | POD{1 |2}
        | BUS{1 | 2}
        | FUNCtion
        | MATH| SBUS}
        <n> ::= 1-2 or 1-4 in NR1 format
        """
        return self.ask(":STAT? %s ;"%disp)

    def qTER(self):
        return self.ask(":TER?;")

    def clear(self):
        self.write("*CLS;")
        
    def wait(self):
        self.write("*WAI;")
        
    def device_clear(self,flags=0,lock_timeout=0,io_timeout=5):
        cVXI11.Vxi11Device.clear(self, flags, lock_timeout, io_timeout)

    def clear_all(self):
        self.clear()
        self.device_clear()
        
    def get_cursor_mode(self):
        return self.ask(":MARK:MODE?;")

    def set_cursor_mode(self,mode="OFF"):
        return self.write(":MARK:MODE %s;"%mode)

    def get_cursor_x1pos(self):
        return self.ask(":MARK:X1P?;")

    def set_cursor_x1pos(self,pos="0"):
        return self.write(":MARK:X1P %s;"%mode)

    def get_cursor_x2pos(self):
        return self.ask(":MARK:X2P?;")

    def set_cursor_x2pos(self,pos="0"):
        return self.write(":MARK:X2P %s;"%mode)

    def get_cursor_xdelta(self):
        return self.ask(":MARK:XDEL?;")
    
    def get_cursor_y1pos(self):
        return self.ask(":MARK:Y1P?;")

    def set_cursor_y1pos(self,pos="0"):
        return self.write(":MARK:Y1P %s;"%mode)

    def get_cursor_y2pos(self):
        return self.ask(":MARK:Y2P?;")

    def set_cursor_y2pos(self,pos="0"):
        return self.write(":MARK:Y2P %s;"%mode)

    def get_cursor_ydelta(self):
        return self.ask(":MARK:YDEL?;")
    #
    def set_wf_ByteOrder(self,order="LSBF"):
        "order = LSBF | MSBF"
        self.write(":WAV:BYT %s;"%order)

    def get_wf_ByteOrder(self):
        "order = LSBF | MSBF"
        return self.ask(":WAV:BYT?;")
        
    def get_wf_format(self):
        "fmt = ASCII|WORD | BYTE"
        return self.ask(":WAV:FORM?;")

    def set_wf_format(self,fmt="ASCII"):
        "fmt = ASCII|WORD | BYTE"
        self.write(":WAV:FORM %s;"%fmt)

    def set_wf_binary(self,fmt="BYTE"):
        "fmt = WORD | BYTE"
        self.write(":WAV:FORM %s;"%fmt)

    def set_wf_ascii(self):
        self.write(":WAV:FORM ASCII;")
        
    def get_wf_point(self):
        return self.ask(":WAV:POIN?;")

    def set_wf_point(self,point="1000"):
        """
        <# points> ::= {100 | 250 | 500 |1000 | <points_mode>} if waveformpoints mode is NORMal
        <# points> ::= {100 | 250 | 500 |1000 | 2000 ... 8000000 in 1-2-5sequence | <points_mode>} ifwaveform points mode is MAXimum or RAW
        <points_mode> ::= {NORMal |MAXimum | RAW}
        The raw acquisition record can only betransferred when the oscilloscope is not running and can only beretrieved from the analog or digital sources.
        """
        self.write(":WAV:POIN %s;"%point)

    def get_wf_point_mode(self):
        return self.ask(":WAV:POIN:MODE?;")

    def set_wf_point_mode(self,mode="NORM"):
        """
        mode=NORM | MAAX| RAW
        """
        self.write(":WAV:POIN:MODE %s;"%mode)

    def get_wave_preamble(self):
        """
        <preamble_block> ::= <formatNR1>, <type NR1>,<pointsNR1>,<count NR1>,
        <xincrementNR3>, <xorigin NR3>, <xreferenceNR1>,
        <yincrement NR3>, <yoriginNR3>, <yreference NR1>
        <format> ::= an integer in NR1format:
          0 for BYTE format
          1 for WORD format
          2 for ASCii format
        <type> ::= an integer in NR1format:
          0 for NORMal type
          1 for PEAK detect type
          2 for AVERage type
          3 for HRESolution type
        <count> ::= Average count, or 1if PEAK detect type or NORMal; aninteger in NR1 format
        """
        return wpreamble(self.ask(":WAV:PRE?;"))
    
    def get_waveform(self,ch=1,io_timeout=5,requestSize=4096):
        """
        it is better to stop scanning before get waveform data on TDS.
        """
        if (type(ch) == bytes):
            self.write(":WAV:SOUR %s;\n"%ch)
        else:
            self.write(":WAV:SOUR CHAN%d;\n"%ch)
            
        import time
        header=self.get_wave_preamble()
        enc=self.get_wf_format().strip()
        byteo=self.get_wf_ByteOrder().strip()
        self.write(":WAV:DATA?;\n")
        r=self.readResponce(io_timeout=io_timeout,requestSize=requestSize)
        wf=waveform(r,format=enc,byteo=byteo,preamble=header)
        return wf

    def get_curve(self,ch=1,io_timeout=5,requestSize=4096):
        self.write(":WAV:SOUR CHAN%d;\n"%ch)
        self.write(":WAV:DATA?")
        return self.readResponce(io_timeout=io_timeout,requestSize=requestSize)

    def get_SESR(self):
        self.write("*ESR?;")
        return SESR(int(self.read()))

    def get_SBR(self):
        self.write("*STB?;")
        return SBR(int(self.read()))

    def get_DESER(self):
        self.write(":DESE?;")
        return DESER(self.read())

    def get_ESER(self):
        self.write("*ESE?;")
        return ESER(self.read())

    def get_SRER(self):
        self.write("*SRE?;")
        return SRER(self.read())

    def SERIAL(self):
        return self.ask(":SER?")

    def VIEW(self,source="CHAN1"):
        self.write(":VIEW %s"%srouce)

    def BLANK(self,source="CHAN1"):
        self.write(":BLANK %s"%srouce)
    
    def AUT(self,*sources):
        """
        Root Autoscale command
        """
        if sources:
            self.write(":AUT %s"%", ".join(sources))
        else:
            self.write(":AUT")
    
    def check_SRQ_source(self):
    # after SRQ occured, srq source registers should be examined to reset
        TER=int(self.ask("TER?"))
        STB=int(self.ask("*STB?"))
        ESR=int(self.ask("*ESR?"))
        OPR=int(self.ask(":OPER?"))
        OPRC=int(self.ask(":OPER:COND?"))
        AER=int(self.ask(":AER?"))
        OVLR=int(self.ask(":OVLR?"))
        return dict(TER=TER, STB=STB, ESR=ESR, 
                    OPR=OPR, OPRC=OPRC, AER=AER, OVLR=OVLR
                    )

def bit(n,d):
    return (d>>n)&1
    
class Register:
    def __init__(self,ini_data):
        self.val=int(ini_data)
    def __str__(self):
        s=""
        for item in list(self.__dict__.items()):
            if item[0] == "val":
                continue
            s+="%s:%d, "%item
        return s

class SESR(Register):
    """Standard Event Status Register
    bit7...................................bit.0
    PON | URQ | CME | EXE | DDE| QYE| RQC | OPC
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.pon=bit(7,self.val)
        self.urq=bit(6,self.val)
        self.cme=bit(5,self.val)
        self.exe=bit(4,self.val)
        self.dde=bit(3,self.val)
        self.qye=bit(2,self.val)
        self.rqc=bit(1,self.val)
        self.opc=bit(0,self.val)
        
class SBR(Register):
    """Status Byte Register
    bit7..................................bit.0
    - | RQS/MSS | ESB| MAV | - |  - |  - |  - 
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.rqs=bit(6,self.val)
        self.mss=bit(6,self.val)
        self.esb=bit(5,self.val)
        self.mav=bit(4,self.val)

class DESER(Register):
    """ Device Event Status Enable Register"
    bit7..................................bit.0
    PON | URQ | CME | EXE | DDE | QYE | RQC | OPC
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.pon=bit(7,self.val)
        self.urq=bit(6,self.val)
        self.cme=bit(5,self.val)
        self.exe=bit(4,self.val)
        self.dde=bit(3,self.val)
        self.qye=bit(2,self.val)
        self.rqc=bit(1,self.val)
        self.opc=bit(0,self.val)

class ESER(Register):
    """ Event Status Enable Register"
    bit7..................................bit.0
    PON | URQ | CME | EXE | DDE | QYE | RQC | OPC
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.pon=bit(7,self.val)
        self.urq=bit(6,self.val)
        self.cme=bit(5,self.val)
        self.exe=bit(4,self.val)
        self.dde=bit(3,self.val)
        self.qye=bit(2,self.val)
        self.rqc=bit(1,self.val)
        self.opc=bit(0,self.val)

class SRER(Register):
    """ Service Request Enable Register"
    bit7...........................bit.0
    - | - | ESB | MAV | - | - | - | -
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.esb=bit(5,self.val)
        self.mav=bit(4,self.val)
#
# data objects
#
class wpreamble:
    pre_block=(
        ("format",int),
        ("type", int),
        ("points",int),
        ("count", int),
        ("xincrement",float),
        ("xorigin",float),
        ("xreference",int),
        ("yincrement",float),
        ("yorigin",float),
        ("yreference",int)
        )
    def __init__(self, data):
        self.str=data
        list=data.split(",")
        for i in range(len(list)):
            key,conv=self.pre_block[i]
            self.__dict__[key]=conv(list[i])

class waveform:
    BFMT={"ASCII":"%d","ASC":"%d","BYTE":"B","WORD":"H"}
    BORD={"MSBF":">","LSBF":"<"}
    DWIDTH={"ASCII":0,"ASC":0,"BYTE":1,"WORD":2}

    def __init__(self,data,format="ASC",byteo="LSBF",preamble=None):
        if preamble:
            if type(preamble) == type(""):
                self.preamble=wpreamble(preamble)
            elif isinstance(preamble,wpreamble):
                self.preamble=preamble
            else:
                raise TypeError("invalid preamble")
        else:
            self.preamble=None
        if data[0] != "#":
            raise ValueError("invalid format")
        hdsize=int(data[1])
        self.dsize=int(data[2:][:hdsize])
        self.rdata=data[2:][hdsize:]
        if (len(self.rdata) < self.dsize):
            raise ValueError("Not enough data %d of %d "%(self.dsize,len(self.rdata)))
        self.ENC=format # ASC|BYTE|WORD
        self.point_fmt=format
        self.BYTE_ORDER=byteo
        self.BIN_FMT=format

        self.Data_Num=self.dsize
        #self.wfid=self.rdata[6]
        if self.preamble:
            self.X_Incr=self.preamble.xincrement
            self.Point_Offset=self.preamble.xreference
            self.X_Zero=self.preamble.xorigin
            if (self.ENC == "ASC"):
                self.Y_Mult=1
                self.Y_Zero=0
                self.Y_Offset=0
            else:
                self.Y_Mult=self.preamble.yincrement
                self.Y_Zero=self.preamble.yorigin
                self.Y_Offset=self.preamble.yreference
        else:
            self.X_Incr=1
            self.Point_Offset=0
            self.X_Zero=0
            #self.X_Unit=self.rdata[11]
            self.Y_Mult=1
            self.Y_Zero=0
            self.Y_Offset=0
            #self.Y_Unit=self.rdata[15]
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.conv_fmt=float
            self.wfsize=len(self.rdata.split(","))
        else:
            self.conv_fmt=self.BORD[self.BYTE_ORDER]+self.BFMT[self.BIN_FMT]
            self.wfsize=self.dsize
        self._convert()

        
    def update(self,curve):
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.wfsize=""
            if (curve[0] == ":"):
                self.rdata=curve[len(":CURVE "):-1]
            else:
                self.rdata=curve[:-1]
        else:
            if (curve[0] == "#"):
                sz=2+int(curve[1])
                self.wfsize=dsz=int(curve[2:sz])
                self.rdata=curve[sz:-1]
            else:
                self.rdata=curve[:-1]
        self._convert()

    def _convert(self):
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.wf=[float(x) for x in self.rdata.split(",")]
        else:
            self.byte_width=self.DWIDTH[self.ENC]
            # self.wf=[struct.unpack(self.conv_fmt,self.rdata[i:i+self.byte_width])[0]
            #          for i in range(0,self.dsize*self.byte_width, self.byte_width)]
            self.wf=numpy.fromstring(self.rdata,
                                     dtype=np.uint,
                                     count=self.dsize, sep='')
        self.y=[((y-self.Y_Offset)*self.Y_Mult+self.Y_Zero) for y in self.wf]
        self.x=[ (x*self.X_Incr+self.X_Zero) for x in range(len(self.y))]
        
    def trace(self):
        return list(zip(self.x,self.y))

class AglCursor:
    def __init__(self,data):
        ent=data.split(";")
        self.function=ent[0]
        self.mode=ent[1]
        self.unit=ent[2]
        self.vpos=(float(ent[3]),float(ent[4]),float(ent[5]))
        self.hdelta=float(ent[6])
        self.select=ent[7]
        self.hpos=(float(ent[8]),float(ent[9]))
        self.hbarspos=(float(ent[10]),float(ent[11]),float(ent[12]))

def test(hostip="10.8.47.30"):
    import Gnuplot
    agl=AglDSO(hostip)
    #agl.set_fulldata()
    gp=Gnuplot.Gnuplot()
    return test_run(agl,gp)

def test_run(agl,gp):
    #runstate=agl.qAcqState()
    #stopafter=agl.qAcqStopAfter()
    agl.Stop()
    #agl.set_AcqStopAfter("SEQ")
    agl.Run();
    while( agl.qOPC()[0] != "1"):
        continue
    agl.Stop()
    wf1,wf2=test_update(agl,gp)
    #agl.set_AcqStopAfter(stopafter)
    #agl.set_AcqState(runstate)
    return (agl,wf1,wf2,gp)

def test_update(agl,gp):
    agl.Run();
    while( agl.qOPC()[0] != "1"):
        continue
    agl.Stop()
    wf1=agl.get_waveform("CH1")
    wf2=agl.get_waveform("CH2")
    gp.title("Python VXI-11 module example \\n from %s"%agl.Model)
    gp.plot(wf1.trace()[:-1],wf2.trace()[:-1])
    return (wf1,wf2)

if __name__ == "__main__":
    test("10.8.46.23")
    """
    host:osc-mon-01.mr.jkcont
    ip:10.64.105.65
    MAC:00-30-d3-10-55-18

    host:osc-mon-02.mr.jkcont
    ip:10.64.105.66
    MAC:00-30-d3-10-55-19
    
    """
    messages=(
#        "*RST;*CLS;\n", 
        ":ACQUIRE:TYPE NORMAL;\n", 
        ":ACQUIRE:MODE SEGMENTED;\n", 
        ":ACQUIRE:SEGMENTED:COUNT 10;\n", 
        ":TRIGGER:SWEEP NORMAL;\n", 
        ":TRIGGER:EDGE:SOURCE CHANNEL1;\n", 
        ":TRIGGER:EDGE:SLOPE NEGATIXOVE;\n", 
        ":TRIGGER:EDGE:LEVEL 1E+0;\n", 
        ":TIMEBASE:SCALE 1E-4;\n", 
        ":CHANNEL1:SCALE 1E+0;\n", 
        ":CHANNEL1:OFFSET 1E+0;\n", 
        ":CHANNEL1:DISPLAY ON;\n", 
        ":DISPLAY:CLEAR;\n", 
        ":WAVEFORM:FORMAT ASCII;\n", 
        )

def test_segment(ip="10.8.47.30"):
    dso=AglDSO(ip)
    messages=(
        "*RST;*CLS;\n", 
        ":ACQUIRE:TYPE NORMAL;\n", 
        ":ACQUIRE:MODE SEGMENTED;\n", 
        ":ACQUIRE:SEGMENTED:COUNT 10;\n", 
        ":TRIGGER:SWEEP NORMAL;\n", 
        ":TRIGGER:EDGE:SOURCE CHANNEL1;\n", 
        ":TRIGGER:EDGE:SLOPE NEGATIVE;\n", 
        ":TRIGGER:EDGE:LEVEL 1E+0;\n", 
        ":TIMEBASE:SCALE 1E-4;\n", 
        ":CHANNEL1:SCALE 1E+0;\n", 
        ":CHANNEL1:OFFSET 1E+0;\n", 
        ":CHANNEL1:DISPLAY ON;\n", 
        ":DISPLAY:CLEAR;\n", 
        ":WAVEFORM:FORMAT ASCII;\n", 
#        "*OPC?;\n", 
        )

    for message in messages:
        sys.stdout.write(message)
        time.sleep(0.2)
        dso.write(message)
    sys.stdout.write("%s"%dso.ask("*OPC?\n", io_timeout=30000))
    dso.write(":SINGLE;\n")
    return dso

def get_segment(dso,n):
    dso.write(":ACQuire:SEGMented:INDex %d ;\n"%n)
    dso.write(":WAVEFORM:DATA?;\n")
    r=dso.readResponce()
    return r
