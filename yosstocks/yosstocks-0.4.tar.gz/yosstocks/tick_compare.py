import TickersData
from matplotlib import pyplot
import pandas
import ctir

#compares visual about tickers
def tick_compare(f_date,t_date,tickers,madad):
    
    d_df=pandas.date_range(f_date,t_date).to_series()
    d_df=d_df.rename("date")#saves all the dates between 2 dates
    d_df=d_df.apply(lambda x: str(x)[:10]).to_frame()#first 10 chars

    for ticker in tickers:
        df=TickersData.get_data_for_ticker_in_range\
            (ticker,f_date,t_date,[madad])#extract data
        final=d_df.merge(df,how="left")
        final=final.fillna(method='ffill')#na<-put last value before
        final.final=["date",ticker+" name",ticker]
        pyplot.plot(final["date"],final[ticker])
    
    #use the function ctir to print summary    
    ctir.ctir(f_date,t_date,tickers)
    pyplot.legend(bbox_to_anchor=(1,1),loc=2)#see all tickers
    pyplot.title(', '.join(tickers))#create a title
    pyplot.ylabel('{} values in period'.format(madad))
    pyplot.yticks(rotation=45)
    pyplot.xticks(rotation=45)
    pyplot.show()

#tick_compare("2018-01-03","2018-03-01",["msft","gooG"],"close")
