import pandas
import numpy
import urllib.request as http
from datetime import datetime
from collections import OrderedDict
import json 
import os
from matplotlib import pyplot

#user name for data from site
user='Y5YHR7BWFGANIN1J'

#saves the data as csv and returns it
def _new_save(ticker_name,send_type,path):
    
    send="https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}".\
    format(ticker_name)+"&outputsize={}&apikey={}".format(send_type,user)#the request to send     
    try:
        response=http.urlopen(send)#the response of the request
        data = json.loads(response.read())['Time Series (Daily)']#parsing the data
    except:
        raise Exception("wrong ticker name")           
    df=pandas.DataFrame(data).T
    df=df.reset_index()#saving the date as column
    df.columns=numpy.insert(["open","high","low","close","volume"],0,"date")
    folder=os.getcwd()+"/data"
    if not os.path.exists(folder):
        os.makedirs(folder)#creates dir for the first time
    df.to_csv(path, index=False)
    return df

#collects data saves as csv an returns to user


def fetch_ticker(ticker_name,timerange=''):

    path=os.getcwd()+"/data/{}.csv".format(ticker_name.upper())#the path to save
    if os.path.exists(path):
        if timerange!='' and timerange!='full':#check that the options are correct
            raise Exception("timerange is wrong")
        else:
            if timerange=='full':#all history
                df=pandas.read_csv(path)
                return df
            else:
                df=pandas.read_csv(path).reset_index().iloc[-100:].drop(["index"],axis=1)#last 100
                return df
    else:
        if timerange=='':
            send_type="compact"
        else:
            send_type=timerange   
        return _new_save(ticker_name,send_type,path)

#get data in range and save it
def get_data_for_ticker_in_range(ticker_name,from_date,to_date,data_type):
    
    try:#check for correct data format
        datetime.strptime(from_date,"%Y-%m-%d")
        datetime.strptime(to_date,"%Y-%m-%d")
    except:
        raise Exception("dates only in format YYYY-MM-DD")
    
    path=os.getcwd()+"/data/{}.csv".format(ticker_name.upper())

    if not os.path.exists(path): 
        df=_new_save(ticker_name,'full',path)
    else:
        df=pandas.read_csv(path)
    try:
        start=df.index[df['date']==from_date].tolist()[0]#start date
        end=df.index[df['date']==to_date].tolist()[0]+1#end date
    except:
        raise Exception("missing data in range of time") 
    try:
        df = df.iloc[start:end].reset_index()
        df["ticker"]=ticker_name
        columns=list(OrderedDict.fromkeys(["date","ticker"]+data_type))#remain in order date first
        return df[columns]
    except:
        raise Exception("no columns like this")
    
# print(get_data_for_ticker_in_range('goog','2018-01-02','2018-03-01',["date","low","open","close","date","close"]))
    
#returns the profit for the user about a ticker in range of dates
def get_profit_for_ticker_in_range(ticker_name,from_date,to_date,accumulated=False):
    
    df=get_data_for_ticker_in_range(ticker_name,from_date,to_date,["close"])
    df["close"]=df["close"].astype('float')#data comes as string cast to double
    shifted=df["close"].shift(1)#python function for shifting one cell
    if accumulated==True:
        df["profit"]=df["close"]/shifted-1#relative profit
        df["Accumulated_profit"]=df[["profit"]].cumprod()[:]["profit"]#accumulated
        df=df[["date","ticker","Accumulated_profit"]]
        return df
    else:
        df["profit"]=df["close"]/shifted-1
        df=df[["date","ticker","profit"]]
        return df
    
#print(get_profit_for_ticker_in_range('goog','2018-01-02','2018-03-01'))

#calculates peak to vally about a ticker in range of time
def get_p2v_for_ticker_in_range(ticker_name,from_date,to_date):
    
    df=get_data_for_ticker_in_range(ticker_name,from_date,to_date,["close"])
    df["close"]=df["close"].astype("float")#cast to float from string
    i_max=df["close"].idxmax()
    i_min=df.iloc[i_max:]["close"].idxmin()#min after maximum
    v_max=df.iloc[i_max]["close"]
    v_min=df.iloc[i_min]["close"]
    s_d=datetime.strptime(to_date,"%Y-%m-%d")
    l_d=datetime.strptime(from_date,"%Y-%m-%d")
    days_diff=s_d-l_d
    days_diff=days_diff.days
    return "{0:.4f}".format(v_max-v_min), "{0:.4f}".format(v_max),"{0:.4f}".format(v_min), days_diff
    
#print(get_p2v_for_ticker_in_range('goog','2018-01-02','2018-03-01'))

# print all the tickers
def tod(day, tickers):
    for ticker in tickers:
        # check that a date is correct
        try:
            date = datetime.strptime(day, "%Y-%m-%d")
        except:
            raise Exception("send a correct date")
        # bring day before to calculate profit of today
        day_before = (date - datetime.timedelta(1)).strftime("%Y-%m-%d")

        try:  # data exist for yestraday
            df = get_profit_for_ticker_in_range(ticker, day_before, day)
        except:  # only today
            df = get_profit_for_ticker_in_range(ticker, day, day)
        # get data using module
        df2 = get_data_for_ticker_in_range(ticker, day, day, ["close"])
        df = df2.merge(df, how="left", on="date")  # left join to match today only
        print("ticker: {}, close: {}, profit: {}".format(ticker, \
                                                         round(df.iloc[0]["close"], 4), round(df.iloc[0]["profit"], 4)))

# compares visual about tickers
def tick_compare(f_date, t_date, tickers, madad):
    d_df = pandas.date_range(f_date, t_date).to_series()
    d_df = d_df.rename("date")  # saves all the dates between 2 dates
    d_df = d_df.apply(lambda x: str(x)[:10]).to_frame()  # first 10 chars

    for ticker in tickers:
        df = get_data_for_ticker_in_range \
            (ticker, f_date, t_date, [madad])  # extract data
        final = d_df.merge(df, how="left")
        final = final.fillna(method='ffill')  # na<-put last value before
        final.final = ["date", ticker + " name", ticker]
        pyplot.plot(final["date"], final[ticker])

    # use the function ctir to print summary
    ctir(f_date, t_date, tickers)
    pyplot.legend(bbox_to_anchor=(1, 1), loc=2)  # see all tickers
    pyplot.title(', '.join(tickers))  # create a title
    pyplot.ylabel('{} values in period'.format(madad))
    pyplot.yticks(rotation=45)
    pyplot.xticks(rotation=45)
    pyplot.show()

# tick_compare("2018-01-03","2018-03-01",["msft","gooG"],"close")

# save data in a path with format
def f4t(f_date, t_date, ticker, route, file):
    file = file.lower()  # consistent name lower case

    if file != "json" and file != 'csv':  # only csv and json are ok
        raise Exception("the file format is wrong")
    else:
        if "\\" in route:  # not accept double backslashes
            raise Exception("enter a route with slash inseted of double backslash")
        if "/" in route:  # this means there is a path
            p1_split = route.split("/")
            name = p1_split[len(p1_split) - 1]  # name out
            route = "/".join(p1_split[:-1])
        else:
            if route == None:  # empty - kickout
                raise Exception("no file name entered")
            else:
                name = route
                route = os.getcwd()
                # false warning about df because the eval function (last row of code)
        df = get_data_for_ticker_in_range(ticker, f_date, t_date, \
                                                      ["low", "high", "open", "close", "volume"])
        if os.path.exists(route) == False:
            os.makedirs(route)
        route = route + "/{}.{}".format(name, file)
        # this function turns string to python code, run according to condition
        eval("df.to_{}(route{})".format(file, ",index=False" if file == 'csv' else ""))

# summary statistics
def ctir(f_date, t_date, tickers):
    for ticker in tickers:
        df = get_data_for_ticker_in_range(ticker, f_date, t_date, ["close"])
        df = df[["close"]].astype("float")
        maxi = df.max()["close"]
        mini = df.min()["close"]
        mean = df.mean()["close"]
        sigma = df.std()["close"]
        profit = df.iloc[df.shape[0] - 1]["close"] / df.iloc[0]["close"]
        # using the created function to calculate p2v
        p2v = get_p2v_for_ticker_in_range(ticker, f_date, t_date)
        print_df = pandas.DataFrame([(ticker, "{0:.4f}".format(profit), \
                                      "{0:.4f}".format(float(p2v[0])), \
                                      maxi, mini, "{0:.4f}".format(mean) \
                                          , "{0:.4f}".format(sigma))], columns= \
                                        ["ticker", "profit", "p2v", "high", "low", "mean", "sigma"])
        print(print_df)
