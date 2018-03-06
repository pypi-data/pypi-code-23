import TickersData
import datetime

#print all the tickers
def tod(day,tickers):
        
    for ticker in tickers:
        #check that a date is correct
        try:
            date=datetime.datetime.strptime(day,"%Y-%m-%d")
        except:
            raise Exception("send a correct date")
        #bring day before to calculate profit of today
        day_before=(date-datetime.timedelta(1)).strftime("%Y-%m-%d")
        
        try:#data exist for yestraday
            df=TickersData.get_profit_for_ticker_in_range(ticker,day_before,day)
        except:#only today
            df=TickersData.get_profit_for_ticker_in_range(ticker,day,day)
        #get data using module
        df2=TickersData.get_data_for_ticker_in_range(ticker,day,day,["close"])
        df=df2.merge(df,how="left",on="date")#left join to match today only
        print("ticker: {}, close: {}, profit: {}".format(ticker,\
              round(df.iloc[0]["close"],4),round(df.iloc[0]["profit"],4)))
