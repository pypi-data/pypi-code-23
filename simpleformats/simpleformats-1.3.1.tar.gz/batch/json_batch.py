import ctxlogger
import datetime
import decimal
import json
import time

from .. import ParseException

class encodejson( json.JSONEncoder ):
    def default( self, o ):
        if isinstance( o, decimal.Decimal ):
            return str( o )
        if isinstance( o, datetime.datetime ):
            return o.strftime( "%Y-%m-%d %H:%M:%S" )
        if isinstance( o, time.struct_time ):
            return time.strftime( "%Y-%m-%d %H:%M:%S", o )
        return super( encodejson, self ).default( o )

class json_batch( object ):
    def parse( self, batch ):
        try:
            return json.loads( batch )
        except Exception as e:
            ctxlogger.exception( ParseException, str(e) )

    def unparse( self, data ):
        try:
            return json.dumps( data, cls = encodejson, ensure_ascii = False )
        except Exception as e:
            ctxlogger.exception( ParseException, str(e) )
