import TickersData
import os

#save data in a path with format
def f4t(f_date,t_date,ticker,route,file):
    
    file=file.lower()#consistent name lower case
    
    if file!="json" and file!='csv':#only csv and json are ok
        raise Exception("the file format is wrong")
    else:    
        if "\\" in route:#not accept double backslashes
            raise Exception("enter a route with slash inseted of double backslash")
        if "/" in route:#this means there is a path
            p1_split=route.split("/")
            name=p1_split[len(p1_split)-1]#name out
            route="/".join(p1_split[:-1])
        else:
            if route==None:#empty - kickout
                raise Exception("no file name entered")
            else:
                name=route
                route=os.getcwd()        
        #false warning about df because the eval function (last row of code)                     
        df=TickersData.get_data_for_ticker_in_range(ticker,f_date,t_date,\
                                             ["low","high","open","close","volume"])
        if os.path.exists(route)==False:
            os.makedirs(route)
        route=route+"/{}.{}".format(name,file)
        #this function turns string to python code, run according to condition
        eval("df.to_{}(route{})".format(file,",index=False" if file=='csv' else ""))
        
        