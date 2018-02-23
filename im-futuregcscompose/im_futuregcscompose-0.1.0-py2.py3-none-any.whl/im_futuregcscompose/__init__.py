from google.cloud import storage  #@UnresolvedImport
from im_future import future, GenerateOnAllChildSuccess, FutureReadyForResult
from im_util import logdebug, logexception, GenerateStableId

def futuregcscompose(gcsbucket=None, gcssourceprefix=None, gcstargetprefix=None, gcstargetfilename="output.txt", onsuccessf=None, onfailuref=None, onprogressf = None, initialresult = None, oncombineresultsf = None, weight = None, parentkey=None, **taskkwargs):
    numgcsfiles = len(list(listbucket(gcsbucket, gcssourceprefix)))
    
    if not numgcsfiles:
        return None
        
    def GCSCombineToTarget(futurekey, startindex, finishindex, istop, **kwargs):
        logdebug("Enter GCSCombineToTarget: %s, %s" % (startindex, finishindex))
        try:
            def higherlevelcompose(lop, rop):
                try:
                    retval = None
                    if lop and rop:
                        blobnames = [lop.get("blobname"), rop.get("blobname")]
                        blobs = getblobsbyname(gcsbucket, *blobnames)
                        if len(blobs) == 2:
                            ltotalcomponent_count = sum([blob.component_count for blob in blobs])
                            logdebug("ltotalcomponent_count: %s" % ltotalcomponent_count)
                            if ltotalcomponent_count > 1020:
                                logdebug("doing copying")
                                newblobnames = ["%s-copy" % blobname for blobname in blobnames]
                                for ix, blob in enumerate(blobs):
                                    try:
                                        copyblob(gcsbucket, blob, newblobnames[ix])
                                    except Exception:
                                        logexception("deleteblobs(copy)")
                                try:
                                    deleteblobs(gcsbucket, blobs)
                                except Exception:
                                    logexception("deleteblobs(copy)")
                                
                                blobnames = newblobnames
                                blobs = getblobsbyname(gcsbucket, *blobnames)
                                                        
                            if len(blobs) == 2:
                                llocalfilename = gcstargetfilename if istop else GenerateStableId(blobnames[0] + blobnames[1])
                                lfilename = "%s/%s-%s" % (gcstargetprefix, "composed", llocalfilename)
                                retval = composeblobs(gcsbucket, lfilename, blobs)
                                retval["count"] = lop.get("count", 0) + rop.get("count", 0)
                                try:
                                    deleteblobs(gcsbucket, blobs)
                                except Exception:
                                    logexception("deleteblobs")
                        else:
                            raise Exception("Can't load blobs")
                    else:
                        retval = lop if lop else rop
                    return retval
                except Exception, ex:
                    logexception("higherlevelcompose")
                    raise ex
            
            onallchildsuccessf = GenerateOnAllChildSuccess(futurekey, None, higherlevelcompose, failonerror=False)
            
            numfiles = finishindex - startindex
            
            if numfiles > 32:
                ranges = CalculateFileRanges(startindex, finishindex, 2)
                logdebug("ranges:%s" % ranges)
                for r in ranges:
                    futurename = "split %s" % (r, )
                    future(GCSCombineToTarget, futurename=futurename, onallchildsuccessf=onallchildsuccessf, parentkey=futurekey, weight = r[1]-r[0], **taskkwargs)(r[0], r[1], False)
                raise FutureReadyForResult()
            else:
                lblobs = list(listbucket(gcsbucket, gcssourceprefix))[startindex:finishindex]
                lfilename = "%s/%s" % (gcstargetprefix, gcstargetfilename if istop else "composed-%s-%s" % (startindex, finishindex))
#                 lfilename = "%s/%s-%s-%s" % (gcstargetprefix, "composed", startindex, finishindex)
                retval = composeblobs(gcsbucket, lfilename, lblobs)
                return retval
        finally:
            logdebug("Leave GCSCombineToTarget: %s, %s" % (startindex, finishindex))
    
    futurename = "gcscombinetotarget %s" % (numgcsfiles)

    return future(GCSCombineToTarget, futurename=futurename, onsuccessf = onsuccessf, onfailuref = onfailuref, onprogressf = onprogressf, parentkey=parentkey, weight = numgcsfiles, **taskkwargs)(0, numgcsfiles, True)


def listbucket(gcsbucket, gcsprefix):
    lgcsclient = storage.Client()
    bucket = lgcsclient.get_bucket(gcsbucket)
    return bucket.list_blobs(prefix = gcsprefix)


def getblobsbyname(gcsbucket, *blobnames):
    lgcsclient = storage.Client()
    bucket = lgcsclient.get_bucket(gcsbucket)
    retval = [bucket.get_blob(blobname) for blobname in blobnames]
    retval = [blob for blob in retval if blob]
    return retval

def deleteblobs(gcsbucket, blobs):
    lgcsclient = storage.Client()
    bucket = lgcsclient.get_bucket(gcsbucket)
    bucket.delete_blobs(blobs)
    
def copyblob(gcsbucket, oldblob, newblobname):
    lgcsclient = storage.Client()
    bucket = lgcsclient.get_bucket(gcsbucket)
    newblob = bucket.blob(newblobname)
    newblob.content_type = "text/plain"

    oldblobbuffer = oldblob.download_as_string()
    newblob.upload_from_string(oldblobbuffer)

def composeblobs(gcsbucket, newblobname, blobs):
    lgcsclient = storage.Client()
    bucket = lgcsclient.get_bucket(gcsbucket)
    ltotalcomponent_count = sum([blob.component_count for blob in blobs if blob and blob.component_count])
    newblob = bucket.blob(newblobname)
    newblob.content_type = "text/plain"
    newblob.compose(blobs)
    return {
        "blobname": newblobname,
        "count": len(blobs),
        "component_count": ltotalcomponent_count
    }

def CalculateFileRanges(startindex, finishindex, numranges):
    amount = finishindex - startindex
    partitions = [((i * amount) / numranges) + startindex for i in range(numranges)] + [finishindex]
    ranges = [(partitions[i], partitions[i+1]) for i in range(numranges)]
    return ranges
