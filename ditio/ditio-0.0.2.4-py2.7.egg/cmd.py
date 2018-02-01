# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 20 2017, 18:23:56) 
# [GCC 5.4.0 20160609]
# Embedded file name: /home/sven/0/_projects/dit.io/ditio/cmd.py
# Compiled at: 2018-01-05 19:46:48
import sys, traceback
from . import *
from . import site
from . import notebook 
from . import log, trace,set_trace, set_debug  

def dispatch(opt, params, mappings):
    fn_keys = [ k for k in mappings.keys() if opt in  k.split(",")  ]
    if len(fn_keys) < 1:
        raise Exception('Invalid options : %s' % str(opt))

    if "--verbose" in fn_keys:
        fn_keys.remove("--verbose") 
        set_verbose(True) 
    fn = mappings[fn_keys[0]]
    fn(params)


class CommandLine(object):

    @staticmethod
    def extract(args):
        opts = [ o for o in args if o.find('-') ==0 ]
        params = [ p for p in args if p.find('-') != 0  ]
        return (opts, params)
    @staticmethod
    def opts(opts):
        options = {} 
        for o in opts:
            k = o 
            v = None 
            if o.find("=") > -1:
               k,v = o.split("=",1)
            options.update({k.replace("--",""):v} )

        return options
    def new(args):
        opts, params = CommandLine.extract(args)
        CommandLine.set_logging(opts) 
        log ( "(command-line): options=%s,parameters=%s " % (opts,params)       ) 
        site.new(params) 

    def preview(args):
        opts, params = CommandLine.extract(args)
        CommandLine.set_logging(opts) 
        operation = opts[0]
        log ( "(command-line): options=%s,parameters=%s " % (opts,params)       ) 

    def publish(args):
        opts, params = CommandLine.extract(args)
        CommandLine.set_logging(opts) 
        operation = opts[0]

        log ( "(command-line): options=%s,parameters=%s " % (opts,params)       ) 
        if "--notebook" in opts:
            notebook.publish(params)
        if "--markdown" in opts: 
            pass 

    def server(args):
        opts, params = CommandLine.extract(args)
        CommandLine.set_logging(opts) 
        log ( "(command-line): options=%s,parameters=%s " % (opts,params)       ) 
  
        options = {"address":"127.0.0.1", "port":"9090"}
        options.update(CommandLine.opts(opts)) 
        log("(command-line-options): %s" % options) 

        site.server(params,options) 
    def preview(args):
        opts, params = CommandLine.extract(args)
        CommandLine.set_logging(opts) 
        log ( "(command-line): options=%s,parameters=%s " % (opts,params)       ) 
        notebooks = params
        site_name = "_preview.io" 


       

        args = ["new",site_name] 
        call(args) 

        for notebook in  notebooks: 
            args = ["publish","--notebook",notebook,site_name] 
            call(args) 

        args = ["index",site_name] 
        call(args) 

        args = ["server","--port=10100",site_name] 
        call(args) 

    def index(args):
        opts, params = CommandLine.extract(args)
        CommandLine.set_logging(opts) 
        log ( "(command-line): options=%s,parameters=%s " % (opts,params)       ) 
        site.index(params)

    @staticmethod 
    def set_logging(opts):
        for o in opts:
            if o.find("--verbose") == 0:
                level = o.split("=")[1]
                if level == '0':
                    set_debug(True) 
                    set_trace(True)
                if level == '1':
                    set_debug(True) 

call = lambda args: CommandLine.__getattribute__(CommandLine, args[0])(args[1:])
# okay decompiling cmd.pyc
