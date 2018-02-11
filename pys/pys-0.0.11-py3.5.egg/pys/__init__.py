'''
pys -- pythons
'''
import re;
try:
    import cPickle as pickle;
except ImportError:
    import pickle;

def conv(arg,default=None,func=None):
    '''
    essentially, the generalization of
    
    arg if arg else default

    or

    func(arg) if arg else default
    '''
    if func:
        return func(arg) if arg else default;
    else:
        return arg if arg else default;

def test(d,k):
    '''short for `k in d and d[k]', returns None otherwise.'''
    if k in d and (d[k] is not False and d[k] is not None):
        return True;

def testN(d,k):
    '''short for `k in d and d[k] is not None', returns None otherwise.'''
    if k in d and (d[k] is not None):
        return True;


def dump_pickle(name, obj):
    '''quick pickle dump similar to np.save'''
    with open(name,"wb") as f:
        pickle.dump(obj,f,2);
    pass;

def load_pickle(name):
    '''quick pickle load similar to np.load'''
    with open(name,"rb") as f:
        return pickle.load(f);
    pass;

def chunks(l,n):
    '''chunk l in n sized bits'''
    #http://stackoverflow.com/a/3226719
    #...not that this is hard to understand.
    return [l[x:x+n] for x in range(0, len(l), n)];

def check_vprint(s, vprinter):
    '''checked verbose printing'''
    if vprinter is True:
        print(s);
    elif callable(vprinter):
        vprinter(s);

def mkvprint(opts):
    '''makes a verbose printer for use with docopts'''
    return lambda s: check_vprint(s,opts['--verbose']);
 
def subcall(cmd):
    '''check output into list'''
    return subprocess.check_output(cmd).split('\n');

def filelines(fname,strip=False):
    '''read lines from a file into lines...optional strip'''
    with open(fname,'r') as f:
        lines = f.readlines();
    if strip:
        lines[:] = [line.strip() for line in lines]
    return lines;

fltrx_s=r"[-+]{0,1}\d+\.{0,1}\d*(?:[eE][-+]{0,1}\d+){0,1}";
fltrx=re.compile(fltrx_s);
intrx_s=r"[-+]{0,1}\d+";
intrx=re.compile(intrx_s);
#i for identifier string. Must start with alpha+underscore.
isrx_s = r'[a-zA-Z_]+[\w ]*';
isrx=re.compile(isrx_s);
rgbrx_s = r"\( *(?:{numrx} *, *){{{rep1}}}{numrx} *,{{0,1}} *\)".format(
    rep1=2,
    numrx=fltrx_s);
colrx_s = r"(?:{isrx}|{rgbrx})".format(isrx=isrx_s,rgbrx=rgbrx_s);
colrx=re.compile(colrx_s);

def parse_utuple(s,urx,length=2):
    '''parse a string into a list of a uniform type'''
    if length is not None and length < 1:
        raise ValueError("invalid length: {}".format(length));
    if length == 1:
        rx = r"\( *{urx} *,? *\)".format(urx=urx);
    elif length is None:
        rx = r"\( *(?:{urx} *, *)*{urx} *,? *\)".format(urx=urx);
    else:
        rx = r"\( *(?:{urx} *, *){{{rep1}}}{urx} *,? *\)".format(
            rep1=length-1,
            urx=urx);
    return re.match(rx,s);

def parse_numtuple(s,intype,length=2,scale=1):
    '''parse a string into a list of numbers of a type'''
    if intype == int:
        numrx = intrx_s;
    elif intype == float:
        numrx = fltrx_s;
    else:
        raise NotImplementedError("Not implemented for type: {}".format(
            intype));
    if parse_utuple(s, numrx, length=length) is None:
        raise ValueError("{} is not a valid number tuple.".format(s));
    return [x*scale for x in eval(s)];

def quote_subs(s, rx=isrx, colorfix=False):
    if colorfix:
        if type(rx) != str:
            rx = rx.pattern;
        return re.sub("(\(|,) *({})".format(rx), '\g<1> "\g<2>"', s);
    return re.sub(rx,'"\g<0>"',s);

def parse_ctuple(s,length=2):
    '''parse a string of acceptable colors into matplotlib, that is, either
       strings, or three tuples of rgb. Don't quote strings.
    '''
    if parse_utuple(s, colrx_s, length=length) is None:
        raise ValueError("{} is not a valid color tuple.".format(s));
    #quote strings
    s=quote_subs(s,colorfix=True);
    return eval(s);

def parse_stuple(s,length=2):
    '''parse a string of strings. Don't quote strings'''
    if parse_utuple(s, srx_s, length=length) is None:
        raise ValueError("{} is not a valid string tuple.".format(s));
    s = quote_subs(s);
    return eval(s);

def parse_ftuple(s,length=2,scale=1):
    '''parse a string into a list of floats'''
    return parse_numtuple(s,float,length,scale);

def parse_ituple(s,length=2,scale=1):
    '''parse a string into a list of floats'''
    return parse_numtuple(s,int,length,scale);

def sd(d,**kw):
    '''
    A hack to return a modified dict dynamically. Basically,
    Does "classless OOP" as in js but with dicts, although
    not really for the "verb" parts of OOP but more of the
    "subject" stuff.

    Confused? Here's how it works:

    `d` is a dict. We have that

    sd(d, perfect=42, gf='qt3.14')

    returns a dict like d but with d['perfect']==42 and
    d['gf']=='qt3.14'. 'sd' stands for "setdefault" which is,
    you know, what we do when we set elements of a dict.
    
    I plan to  use this heavily.
    '''
    #HURR SO COMPLICATED
    r={};        #copy. if you want to modify,
    r.update(d); #use {}.update
    r.update(kw);
    return r;

def savetxt(fname, s=""):
    '''write to a text file'''
    with open(fname,"wb") as f:
        f.write(s);

def readtxt(fname):
    '''read a text file'''
    with open(fname,"rb") as f:
        s = f.read();
    return s;

def take(d,l):
    '''take a list of keys from a dict'''
    return {i:d[i] for i in l};

def destr(d,l):
    '''destructure a dict (like take, but return a list)'''
    return [d[i] for i in l];

def takef(d,l,val=None):
    '''take(f) a list of keys and fill in others with val'''
    return {i:(d[i] if i in d else val)
            for i in l};

def mk_getkw(kw, defaults,prefer_passed=False):
    '''
    a helper for generating a function for reading keywords in
    interface functions with a dictionary with defaults

    expects the defaults dictionary to have keywords you request.

    example:
    defaults = dict(a='a',b=3);
    def bigfunc(**kw):
        getkw=mk_getkw(kw,defaults);

        # I want the callers' `a', or the default if s/he doesn't
        # supply it
        a=getkw('a');
        c = [a]*getkw('b');
        return c,c[0]; 

    Option:
        prefer_passed -- use "l in kw" only, not test.
    '''
    def getkw(*ls):
        r = [ kw[l] if test(kw,l) else defaults[l]
              for l in ls ];
        if len(r) == 1: return r[0];
        return r;
    def getkw_prefer_passed(*ls):
        r = [ kw[l] if l in kw else defaults[l]
              for l in ls ];
        if len(r) == 1: return r[0];
        return r;
    return getkw if not prefer_passed else getkw_prefer_passed;

            

