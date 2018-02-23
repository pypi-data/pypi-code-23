from im_util import logdebug
import cloudstorage as gcs
from im_future import future, GenerateOnAllChildSuccess, setlocalprogress, FutureReadyForResult, generatefuturepagemapf
from im_gcsfilesharded import hwalk

def futuregcsfileshardedpagemap(pagemapf=None, gcspath=None, pagesize=100, onsuccessf=None, onfailuref=None, onprogressf = None, onallchildsuccessf = None, initialresult = None, oncombineresultsf = None, weight = None, parentkey=None, **taskkwargs):
    def MapOverRange(futurekey, startbyte, endbyte, weight, **kwargs):
        logdebug("Enter MapOverRange: %s, %s, %s" % (startbyte, endbyte, weight))

        linitialresult = initialresult if not initialresult is None else 0
        loncombineresultsf = oncombineresultsf if oncombineresultsf else lambda a, b: a + b
    
        try:
            # open file at gcspath for read
            with gcs.open(gcspath) as gcsfile:
                page, ranges = hwalk(gcsfile, pagesize, 2, startbyte, endbyte) 

            if pagemapf:
                lonallchildsuccessf = GenerateOnAllChildSuccess(futurekey, linitialresult, loncombineresultsf)
                taskkwargs["futurename"] = "pagemap %s of %s,%s" % (len(page), startbyte, endbyte)
                future(pagemapf, parentkey=futurekey, onallchildsuccessf=lonallchildsuccessf, weight = len(page), **taskkwargs)(page)
            else:
                setlocalprogress(futurekey, len(page))

            if ranges:
                newweight = (weight - len(page)) / len(ranges) if not weight is None else None 
                for arange in ranges:
                    taskkwargs["futurename"] = "shard %s" % (arange)

                    lonallchildsuccessf = GenerateOnAllChildSuccess(futurekey, linitialresult if pagemapf else len(page), loncombineresultsf)

                    future(MapOverRange, parentkey=futurekey, onallchildsuccessf=lonallchildsuccessf, weight = newweight, **taskkwargs)(arange[0], arange[1], weight = newweight)
                
            if ranges or pagemapf:
                raise FutureReadyForResult("still going")
            else:
                return len(page)
        finally:
            logdebug("Leave MapOverRange: %s, %s, %s" % (startbyte, endbyte, weight))

    # get length of file in bytes
    filestat = gcs.stat(gcspath)

    filesizebytes = filestat.st_size    

    futurename = "top level 0 to %s" % (filesizebytes)

    taskkwargscopy = dict(taskkwargs)
    taskkwargscopy["futurename"] = taskkwargscopy.get("futurename", futurename)

    return future(MapOverRange, onsuccessf = onsuccessf, onfailuref = onfailuref, onprogressf = onprogressf, onallchildsuccessf=onallchildsuccessf, parentkey=parentkey, weight = weight, **taskkwargscopy)(0, filesizebytes, weight)

 
def generategcsinvokemapf(mapf):
    def InvokeMap(futurekey, line, **kwargs):
        logdebug("Enter InvokeMap: %s" % line)
        try:
            return mapf(line, **kwargs)
        finally:
            logdebug("Leave InvokeMap: %s" % line)
    return InvokeMap

def futuregcsfileshardedmap(mapf=None, gcspath=None, pagesize = 100, onsuccessf = None, onfailuref = None, onprogressf = None, onallchildsuccessf=None, initialresult = None, oncombineresultsf = None, weight= None, parentkey = None, **taskkwargs):
    invokeMapF = generategcsinvokemapf(mapf)
    pageMapF = generatefuturepagemapf(invokeMapF, initialresult, oncombineresultsf **taskkwargs)
    return futuregcsfileshardedpagemap(pageMapF, gcspath, pagesize, onsuccessf = onsuccessf, onfailuref = onfailuref, onprogressf = onprogressf, onallchildsuccessf=onallchildsuccessf, initialresult = initialresult, oncombineresultsf = oncombineresultsf, parentkey=parentkey, weight=weight, **taskkwargs)

