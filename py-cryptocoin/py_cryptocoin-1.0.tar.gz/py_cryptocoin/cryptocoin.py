import requests
import logging
import json

class CryptoCoin:
    def __init__(self):
        try:
            # list with shortcodes, it returns the right name
            self.options = {"btc": self.btc(),
                            "eth": self.eth(),
                            "xrp": self.xrp(),
                            "bch": self.bch(),
                            "ada": self.ada(),
                            "ltc": self.ltc(),
                            "xem": self.xem(),
                            "neo": self.neo(),
                            "xlm": self.xlm(),
                            "eos": self.eos(),
                            "miota": self.miota(),
                            "dash": self.dash(),
                            "xmr": self.xmr(),
                            "trx": self.trx(),
                            "btg": self.btg(),
                            "icx": self.icx(),
                            "qtum": self.qtum(),
                            "etc": self.etc(),
                            "lsk": self.lsk(),
                            "xrb": self.xrb(),
                            "ven": self.ven(),
                            "omg": self.omg(),
                            "usdt": self.usdt(),
                            "ppt": self.ppt(),
                            "zec": self.zec(),
                            "xvg": self.xvg(),
                            "sc": self.sc(),
                            "bnb": self.bnb(),
                            "strat": self.strat(),
                            "bcn": self.bcn(),
                            "steem": self.steem(),
                            "ardr": self.ardr(),
                            "snt": self.snt(),
                            "mkr": self.mkr(),
                            "rep": self.rep(),
                            "bts": self.bts(),
                            "kcs": self.kcs(),
                            "waves": self.waves(),
                            "zrx": self.zrx(),
                            "doge": self.doge(),
                            "etn": self.etn(),
                            "veri": self.veri(),
                            "kmd": self.kmd(),
                            "dcr": self.dcr(),
                            "drgn": self.drgn(),
                            "wtc": self.wtc(),
                            "dcn": self.dcn(),
                            "lrc": self.lrc(),
                            "ark": self.ark(),
                            "salt": self.salt(),
                            "qash": self.qash(),
                            "dgb": self.dgb(),
                            "bat": self.bat(),
                            "gnt": self.gnt(),
                            "hsr": self.hsr(),
                            "knc": self.knc(),
                            "gas": self.gas(),
                            "wax": self.wax(),
                            "ethos": self.ethos(),
                            "pivx": self.pivx(),
                            "gbyte": self.gbyte(),
                            "fun": self.fun(),
                            "aion": self.aion(),
                            "rhoc": self.rhoc(),
                            "zcl": self.zcl(),
                            "fct": self.fct(),
                            "smart": self.smart(),
                            "dent": self.dent(),
                            "mona": self.mona(),
                            "elf": self.elf(),
                            "powr": self.powr(),
                            "dgd": self.dgd(),
                            "kin": self.kin(),
                            "rdd": self.rdd(),
                            "ae": self.ae(),
                            "btm": self.btm(),
                            "nas": self.nas(),
                            "sys": self.sys(),
                            "req": self.req(),
                            "nebl": self.nebl(),
                            "link": self.link(),
                            "eng": self.eng(),
                            "xp": self.xp(),
                            "gxs": self.gxs(),
                            "maid": self.maid(),
                            "sub": self.sub(),
                            "xzc": self.xzc(),
                            "nxs": self.nxs(),
                            "nxt": self.nxt(),
                            "med": self.med(),
                            "emc": self.emc(),
                            "btx": self.btx(),
                            "bnt": self.bnt(),
                            "cnd": self.cnd(),
                            "qsp": self.qsp(),
                            "cnx": self.cnx(),
                            "icn": self.icn(),
                            "game": self.game(),
                            "pay": self.pay(),
                            "part": self.part(),
                            }        
        
        
        except Exception as e:
            msg = "def __init__ : " + str(e)
            logging.warning(msg)        
        
    
    def get_url(self, url=None):
        """
        Function to get the url and get the content
        returns decoded utf8 content
        """
        try:
            if url is None:
                raise Exception("No Url")
            
            r = requests.get(url)
            if r.status_code > 200:
                raise Exception("Url " + url + "problem : " + str(r.status_code))
            
            content = r.content.decode("utf8")
            return content
        
        except Exception as e:
            msg = "def get_url : " + str(e)
            logging.warning(msg)            
            
            

    def get_json_from_url(self, url):
        """
        Function to parse the url content into json 
        returns decoded utf8 content
        """
        try:        
            content = self.get_url(url)
            if content is None:
                raise Exception("No Data")
            
            return json.loads(content)
        
        except Exception as e:
            msg = "def get_json_from_url : " + str(e)
            logging.warning(msg)



    def getAllCoinData(self, start=None, limit=None, currency=None):
        """
        Function to get all coin currency data 
        parameters start, limit, currency
        returns decoded utf8 Dict
        """
        try:
            url = "https://api.coinmarketcap.com/v1/ticker/?start={}&limit={}&convert={}".format(start,limit,currency)
            return self.get_json_from_url(url)
        except Exception as e:
            msg = "def getAllCoinData : " + str(e)
            logging.warning(msg)        
        
    
    def getGlobalData(self, currency=None):
        """
        Function to get all coin global data 
        parameters currency
        returns decoded utf8 Dict
        """        
        try:
            url = " https://api.coinmarketcap.com/v1/global/?convert={}".format(currency)
            return self.get_json_from_url(url)
        
        except Exception as e:
            msg = "def getGlobalData : " + str(e)
            logging.warning(msg)
        
    def getCoinData(self, Coin=None, currency=None):
        """
        Function to get one coin currency data 
        parameters cryptocoin shortcode, currency
        returns decoded utf8 Dict
        """             
        try:
            coin = self.options[Coin.lower()]
            url = "https://api.coinmarketcap.com/v1/ticker/{}/?convert={}".format(coin, currency)
            self.data = self.get_json_from_url(url)
        
            return self.data
        
        except Exception as e:
            msg = "def getCoinData : " + str(e)
            logging.warning(msg)
        
        
        
    def returnCoins(self):
        """
            small function for myself to return a coinlist for the README file
            returns list with coins
        """
        try: 
            coinlist = ""
        
            for d in self.data:
                # "rip": self.rip(),
                symbol = d['symbol']
                symbol = symbol.lower()
                
                coinlist += "- '" + symbol + "' : '" + d['name'] + "', "    
            
            return coinlist
            
        except Exception as e:
            msg = "def returnCoins : " + str(e)
            logging.warning(msg)        
    
    
    
    '''
    The Following functions are useless for you, 
    but very handy for the creator of this script
    '''
    def returnOptions(self):
        """
            small function for myself to return a option list for __init__
            returns list with options 
        """        
        try:
            option = ""
            
            for d in self.data:
                # "rip": self.rip(),
                symbol = d['symbol']
                symbol = symbol.lower()
                option += '"' + symbol + '": self.' + symbol + "(),\n"
            
            return option
        except Exception as e:
            msg = "def returnOptions : " + str(e)
            logging.warning(msg)
        
    def returnFunctions(self):
        """
            small function for myself to return a list with functions for the self.options
            returns list with functions 
        """           
        try:
            functie = ""
            
            for d in self.data:
                # "rip": self.rip(),
                symbol = d['symbol']
                symbol = symbol.lower()
                
                functie += "def " + symbol+ "(self):\n"
                functie += "\t return '" + d['id'] + "'\n\n"
        except Exception as e:
            msg = "def returnFunctions : " + str(e)
            logging.warning(msg)        
        
        
        
    """
    some functions to return the right coin name
    """
    def btc(self):
         return 'bitcoin'
    
    def eth(self):
         return 'ethereum'
    
    def xrp(self):
         return 'ripple'
    
    def bch(self):
         return 'bitcoin-cash'
    
    def ada(self):
         return 'cardano'
    
    def ltc(self):
         return 'litecoin'
    
    def xem(self):
         return 'nem'
    
    def neo(self):
         return 'neo'
    
    def xlm(self):
         return 'stellar'
    
    def eos(self):
         return 'eos'
    
    def miota(self):
         return 'iota'
    
    def dash(self):
         return 'dash'
    
    def xmr(self):
         return 'monero'
    
    def trx(self):
         return 'tron'
    
    def btg(self):
         return 'bitcoin-gold'
    
    def icx(self):
         return 'icon'
    
    def qtum(self):
         return 'qtum'
    
    def etc(self):
         return 'ethereum-classic'
    
    def lsk(self):
         return 'lisk'
    
    def xrb(self):
         return 'raiblocks'
    
    def ven(self):
         return 'vechain'
    
    def omg(self):
         return 'omisego'
    
    def usdt(self):
         return 'tether'
    
    def ppt(self):
         return 'populous'
    
    def zec(self):
         return 'zcash'
    
    def xvg(self):
         return 'verge'
    
    def sc(self):
         return 'siacoin'
    
    def bnb(self):
         return 'binance-coin'
    
    def strat(self):
         return 'stratis'
    
    def bcn(self):
         return 'bytecoin-bcn'
    
    def steem(self):
         return 'steem'
    
    def ardr(self):
         return 'ardor'
    
    def snt(self):
         return 'status'
    
    def mkr(self):
         return 'maker'
    
    def rep(self):
         return 'augur'
    
    def bts(self):
         return 'bitshares'
    
    def kcs(self):
         return 'kucoin-shares'
    
    def waves(self):
         return 'waves'
    
    def zrx(self):
         return '0x'
    
    def doge(self):
         return 'dogecoin'
    
    def etn(self):
         return 'electroneum'
    
    def veri(self):
         return 'veritaseum'
    
    def kmd(self):
         return 'komodo'
    
    def dcr(self):
         return 'decred'
    
    def drgn(self):
         return 'dragonchain'
    
    def wtc(self):
         return 'walton'
    
    def dcn(self):
         return 'dentacoin'
    
    def lrc(self):
         return 'loopring'
    
    def ark(self):
         return 'ark'
    
    def salt(self):
         return 'salt'
    
    def qash(self):
         return 'qash'
    
    def dgb(self):
         return 'digibyte'
    
    def bat(self):
         return 'basic-attention-token'
    
    def gnt(self):
         return 'golem-network-tokens'
    
    def hsr(self):
         return 'hshare'
    
    def knc(self):
         return 'kyber-network'
    
    def gas(self):
         return 'gas'
    
    def wax(self):
         return 'wax'
    
    def ethos(self):
         return 'ethos'
    
    def pivx(self):
         return 'pivx'
    
    def gbyte(self):
         return 'byteball'
    
    def fun(self):
         return 'funfair'
    
    def aion(self):
         return 'aion'
    
    def rhoc(self):
         return 'rchain'
    
    def zcl(self):
         return 'zclassic'
    
    def fct(self):
         return 'factom'
    
    def smart(self):
         return 'smartcash'
    
    def dent(self):
         return 'dent'
    
    def mona(self):
         return 'monacoin'
    
    def elf(self):
         return 'aelf'
    
    def powr(self):
         return 'power-ledger'
    
    def dgd(self):
         return 'digixdao'
    
    def kin(self):
         return 'kin'
    
    def rdd(self):
         return 'reddcoin'
    
    def ae(self):
         return 'aeternity'
    
    def btm(self):
         return 'bytom'
    
    def nas(self):
         return 'nebulas-token'
    
    def sys(self):
         return 'syscoin'
    
    def req(self):
         return 'request-network'
    
    def nebl(self):
         return 'neblio'
    
    def link(self):
         return 'chainlink'
    
    def eng(self):
         return 'enigma-project'
    
    def xp(self):
         return 'experience-points'
    
    def gxs(self):
         return 'gxshares'
    
    def maid(self):
         return 'maidsafecoin'
    
    def sub(self):
         return 'substratum'
    
    def xzc(self):
         return 'zcoin'
    
    def nxs(self):
         return 'nexus'
    
    def nxt(self):
         return 'nxt'
    
    def med(self):
         return 'medibloc'
    
    def emc(self):
         return 'emercoin'
    
    def btx(self):
         return 'bitcore'
    
    def bnt(self):
         return 'bancor'
    
    def cnd(self):
         return 'cindicator'
    
    def qsp(self):
         return 'quantstamp'
    
    def cnx(self):
         return 'cryptonex'
    
    def icn(self):
         return 'iconomi'
    
    def game(self):
         return 'gamecredits'
    
    def pay(self):
         return 'tenx'
    
    def part(self):
         return 'particl'