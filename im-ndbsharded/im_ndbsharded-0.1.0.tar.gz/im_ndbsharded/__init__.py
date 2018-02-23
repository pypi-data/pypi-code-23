from im_task import task, RetryTaskException
from im_util import logdebug
from google.appengine.ext.key_range import KeyRange

def ndbshardedpagemap(pagemapf=None, ndbquery=None, initialshards = 10, pagesize = 100, **taskkwargs):
    @task(**taskkwargs)
    def MapOverRange(keyrange, **kwargs):
        logdebug("Enter MapOverRange: %s" % keyrange)
 
        _fixkeyend(keyrange, kind)
 
        filteredquery = keyrange.filter_ndb_query(ndbquery)
         
        logdebug (filteredquery)
         
        keys, _, more = filteredquery.fetch_page(pagesize, keys_only=True)
         
        if pagemapf:
            pagemapf(keys)
                     
        if more and keys:
            newkeyrange = KeyRange(keys[-1], keyrange.key_end, keyrange.direction, False, keyrange.include_end)
            krlist = newkeyrange.split_range()
            logdebug("krlist: %s" % krlist)
            for kr in krlist:
                MapOverRange(kr)
        logdebug("Leave MapOverRange: %s" % keyrange)
 
    kind = ndbquery.kind
 
    krlist = KeyRange.compute_split_points(kind, initialshards)
    logdebug("first krlist: %s" % krlist)
 
    for kr in krlist:
        MapOverRange(kr)

def ndbshardedmap(mapf=None, ndbquery=None, initialshards = 10, pagesize = 100, skipmissing = False, **taskkwargs):
    @task(**taskkwargs)
    def InvokeMap(key, **kwargs):
        logdebug("Enter InvokeMap: %s" % key)
        try:
            obj = key.get()
            if not obj:
                if not skipmissing:
                    raise RetryTaskException("couldn't get object for key %s" % key)
                # else just skip
            else:
                mapf(obj, **kwargs)
        finally:
            logdebug("Leave InvokeMap: %s" % key)
    
    def ProcessPage(keys):
        for index, key in enumerate(keys):
            logdebug("Key #%s: %s" % (index, key))
            InvokeMap(key)

    ndbshardedpagemap(ProcessPage, ndbquery, initialshards, pagesize, **taskkwargs)

def _fixkeyend(keyrange, kind):
    if keyrange.key_start and not keyrange.key_end:
        endkey = KeyRange.guess_end_key(kind, keyrange.key_start)
        if endkey and endkey > keyrange.key_start:
            logdebug("Fixing end: %s" % endkey)
            keyrange.key_end = endkey
