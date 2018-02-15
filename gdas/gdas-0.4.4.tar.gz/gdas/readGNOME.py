# Relies on gwpy.timeseries.{TimeSeries,TimeSeriesList}
#   h5py,time,calendar,os.{listdir,path.{isfile,join}}
from gwpy.timeseries import TimeSeries,TimeSeriesList
import h5py
import time, calendar
from os import listdir
from os.path import isfile, join

def getDataFromFile(fName, convert=False):
    '''
    Gets magnetometer data from file.
    
    fName: str
        Name of file
    convert: boolean (default: False)
        Whether to use conversion function from file.
        
    returns (data, sanity data) as astropy TimeSeries
    
    Note: must evaluate values in 'sanity' (e.g., using 'value' attribute) to get boolean
    '''
    h5pyFile = h5py.File(fName,'r')
    saneList = h5pyFile['SanityChannel']
    dataList = h5pyFile['MagneticFields']
    
    # get mag field attributes
    attrs = dataList.attrs
    sampRate = float(attrs['SamplingRate(Hz)'])
    startT = time.mktime(time.strptime(attrs['Date']+' '+attrs['t0'], '%Y/%m/%d %H:%M:%S.%f'))
    # get sanity attributes
    saneAttrs = saneList.attrs
    saneRate = float(saneAttrs['SamplingRate(Hz)'])
    saneStart = time.mktime(time.strptime(saneAttrs['Date']+' '+saneAttrs['t0'], '%Y/%m/%d %H:%M:%S.%f'))
    
    # create data TimeSeries
    dataTS = TimeSeries(dataList, sample_rate=sampRate, epoch=startT) # put data in TimeSeries
    if(convert):
        convStr = attrs['MagFieldEq'] #string contatining conversion function
        unitLoc = convStr.find('[') # unit info is at end in []
        if(unitLoc >= 0): # unit given
            convStr = convStr[:unitLoc] # get substring before units
        convStr=convStr.replace('MagneticFields','dataTS') # relabel with correct variable
        exec 'dataTS = '+convStr # dynamic execution to convert dataTS
    # create sanity TimeSeries
    saneTS = TimeSeries(saneList, sample_rate=saneRate, epoch=saneStart)
    
    h5pyFile.close()    
    return dataTS, saneTS

def getFListInRange(station, startTime, endTime, path='./', verbose=False):
    '''
    Get list of file names for GNOME experiment within a time period.
    
    Data located in folder of the form 'path/station/yyyy/mm/dd/'.
    Time range uses the start time listed in the 'hdf5' file name.
    
    station: str
        Name of station.
    startTime: float (unix time), str
        Earliest time. String formatted as 'yyyy-mm-dd-HH-MM-SS' (omitted values defaulted as 0)
    endTime: float (unix time), str
        Last time. Format same as startTime
    path: str (default './')
        Location of files
    verbose: bool (default False)
        Verbose output
        
    returns list of file names
    '''
    # put date in consistant format
    makeSU = True # Need to calculate start time in unix
    makeEU = True # Need to calculate end time in unix
    if(not type(startTime) is str): # given unix time
        startUnix = startTime
        makeSU = False
        startTime = time.strftime('%Y-%m-%d-%H-%M-%S',time.gmtime(startTime)) 
    if(not type(endTime) is str): # given unix time
        endUnix = endTime
        makeEU = False
        endTime = time.strftime('%Y-%m-%d-%H-%M-%S',time.gmtime(endTime))
    
    # Format start/end times (in array and unix time, if needed)
    startTList = [0.]*9 # date-time tuples (note that last 3 should never be changed)
    endTList   = [0.]*9
    startTime = str.split(startTime,'-')
    endTime = str.split(endTime,'-')
    startTList[:len(startTime)] = [int(t) if len(t)>0 else 0. for t in startTime]
    endTList[:len(endTime)]     = [int(t) if len(t)>0 else 0. for t in endTime]
    if(makeSU):
        startUnix = calendar.timegm(startTList)
    if(makeEU):
        endUnix = calendar.timegm(endTList)
        
    # check for bad input
    if(startUnix > endUnix):
        if(verbose):
            print 'getFListInRange() --- Bad input time range (check order).'
        return []
    
    # create array of dates (used for folders)
    dummy = [0.]*9
    dummy[0:3] = startTList[0:3] # start date (beginning of day)
    currTime = calendar.timegm(dummy)
    dates = []
    while(currTime < endUnix):
        dates.append(time.strftime('%Y/%m/%d/',time.gmtime(currTime))) # path segment
        currTime += 86400 # add a day
    
    fList = [] #will hold list of files
        
    for i in range(len(dates)):
        firstDate = i==0 # use these bools to skip checks for middle dates
        lastDate = i==len(dates)-1
        
        dataDir = join(path,station,dates[i]) #directory of files from date
        
        try:
            # get list of files (ignore, e.g., folders)
            foldFiles = [f for f in listdir(dataDir) if isfile(join(dataDir, f))]
            
            # add file to list if it is in time range
            # files like: fribourg01_20170102_122226.hdf5
            for f in foldFiles:
                inRange = not (firstDate or lastDate)
                if(not inRange): # need to check
                    fTime = f.split('_')[2].split('.')[0] # get time 'hhmmss'
                    fTime = fTime[0:2]+':'+fTime[2:4]+':'+fTime[4:6] # time format hh:mm:ss
#                     print dates[i]+fTime, f
                    fTime = calendar.timegm(time.strptime(dates[i]+fTime, '%Y/%m/%d/%H:%M:%S')) # in unix
                    if(fTime >= startUnix and fTime < endUnix):
                        inRange = True
#                     print '\t', inRange
                if(inRange): # add file to list
                    fList.append(join(dataDir, f))
                # in case the file list is not sorted, look through all files.
        except OSError:
            if(verbose):
                print 'getFListInRange() --- Data not found for:', dates[i]
    
    return fList

def getDataInRange(station, startTime, endTime, sortTime=True, convert=False, path='./', verbose=False):
    '''
    Get list of data in time range
    
    station: str
        Name of station.
    startTime: float (unix time), str
        Earliest time. String formatted as 'yyyy-mm-dd-HH-MM-SS' 
        (omitted values defaulted as 0)
    endTime: float (unix time), str
        Last time. Format same as startTime
    sortTime: bool (default: True)
        Actively sort output by start time (using data in file)
    convert: boolean (default: False)
        Whether to use conversion function from file.
    path: str (default './')
        Location of files
    verbose: bool (default False)
        Verbose output
    
    returns (data, sanity, fileList). Data and sanity are astropy TimeSeriesList
    
    Note: must evaluate values in 'sanity' (e.g., using 'value' attribute) to get boolean
    Note: use, e.g., dataTSL.join(pad=float('nan'),gap='pad') to combine 
    TimeSeriesList into single Time series.
    '''
    if(verbose):
        print 'getDataInRange() --- Finding files'
    fList = getFListInRange(station, startTime, endTime, path=path)
    numFiles = len(fList)
    
    # get data
    if(verbose):
        print 'getDataInRange() --- Reading files'
    dataList = [None]*numFiles
    saneList = [None]*numFiles
    for i in range(numFiles):
        dataList[i],saneList[i] = getDataFromFile(fList[i],convert=convert)
    
    # sort if needed
    if(sortTime):
        if(verbose):
            print 'getDataInRange() --- Sorting data'
        # do insertion sort (likely that list is sorted)
        sortIndex = range(numFiles) # sorted list of indices
        
        for sRange in range(1, numFiles): # sRange is size of sorted segment
            # note, sortIndex[sRange] = sRange
            insPtTime = dataList[sRange].epoch # for point being inserted
            insHere = sRange # place to insert point
            while(insHere > 0 and dataList[sortIndex[insHere-1]].epoch > insPtTime): 
                insHere -= 1 # decrement until finding place to insert
            # insert point
            dummy1 = sRange # point being moved
            while(insHere <= sRange):
                dummy2 = sortIndex[insHere]
                sortIndex[insHere] = dummy1
                dummy1 = dummy2
                insHere+=1
    else:
        sortIndex = range(numFiles)
    
    # put data in TimeSeriesList
    dataTSL = TimeSeriesList()
    saneTSL = TimeSeriesList()
    for i in sortIndex:
        dataTSL.append(dataList[i])
        saneTSL.append(saneList[i])
    return dataTSL, saneTSL, [fList[i] for i in sortIndex]