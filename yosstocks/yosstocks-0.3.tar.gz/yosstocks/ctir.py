import TickersData
import pandas

#summary statistics
def ctir(f_date,t_date,tickers):
    
    for ticker in tickers:
        df=TickersData.get_data_for_ticker_in_range(ticker,f_date,t_date,["close"])
        df=df[["close"]].astype("float")
        maxi=df.max()["close"]
        mini=df.min()["close"]
        mean=df.mean()["close"]
        sigma=df.std()["close"]
        profit=df.iloc[df.shape[0]-1]["close"]/df.iloc[0]["close"]
        #using the created function to calculate p2v
        p2v=TickersData.get_p2v_for_ticker_in_range(ticker,f_date,t_date)
        print_df = pandas.DataFrame([(ticker,"{0:.4f}".format(profit),\
                                 "{0:.4f}".format(float(p2v[0])),\
                                 maxi,mini,"{0:.4f}".format(mean)\
                                 ,"{0:.4f}".format(sigma))],columns = \
                ["ticker","profit","p2v","high","low","mean","sigma"])
        print(print_df)
        
        
        