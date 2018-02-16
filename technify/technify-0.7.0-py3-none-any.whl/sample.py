from stock import Stock
from portfolio import Portfolio
import yfm
import quandl
quandl.ApiConfig.api_key = 'rw9yfFJxGqkKdsqauyyf'

if __name__ == "__main__":
    y = yfm.fetcher()
    sans = y.getTicker("san.mc")

    #dataeur = quandl.get("BCHARTS/KRAKENEUR")
    #eurdlr = quandl.get("ECB/EURUSD")

    bitusd = Stock()\
                .fromQuandl("BCHARTS/KRAKENUSD", "Close")\
                .addEma(50, "Close")\
                .addEma(200, "Close")\
                .show(range(-60), "Close","ema50", "ema200")

    #p = Portfolio(bitusd)
    #print(p.getBuyAndHold())

