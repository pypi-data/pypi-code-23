"""Configuration file support.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import os
import sys
import platform

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumolib.[module]".
    sys.path.append("..")

import sumolib.JSON

__version__="3.3" #VERSION#

assert __version__==sumolib.JSON.__version__

# -----------------------------------------------
# config file support
# -----------------------------------------------

class ConfigFile(object):
    """store options in a JSON file."""
    @staticmethod
    def paths_from_env(varname):
        """read configuration paths from environment variable."""
        val= os.environ.get(varname)
        if not val:
            return
        # allow ":" and ";" as separators:
        if platform.system()=="Windows":
            sep= ";"
        else:
            sep= ":"
        return val.split(sep)
    @classmethod
    def from_optionlist(cls, filename, env_name, optionlist):
        """Create object from optionlist."""
        d= dict( [(n,None) for n in optionlist])
        return cls(filename, env_name, d)
    def __init__(self, filename, env_name, dict_):
        """create from a dict.

        If filename is not empty, search for config files at:
          /etc
          <path of this python file>
          $HOME
          <cwd>

        """
        self._dict= dict(dict_)
        self._filename= filename
        self._real_paths= []
        if not filename:
            self._paths= []
        else:
            search_paths= self.__class__.paths_from_env(env_name)
            if not search_paths:
                # not specified by environment variable:
                lib_path= os.path.dirname(os.path.abspath(__file__))
                search_paths=["/etc",
                              lib_path,
                              os.environ.get("HOME"),
                              os.getcwd()]
            self._paths= []
            for path in search_paths:
                if not path:
                    continue
                p= os.path.join(path, filename)
                if os.path.isfile(p):
                    self._paths.append(p)
    def __repr__(self):
        """return repr string."""
        return "%s(%s, %s)" % (self.__class__.__name__,
                               repr(self._filename),
                               repr(self._dict))
    def __str__(self):
        """return string in human readable form."""
        lines= ["filename: %s\n" % self._filename,
                "dict:",
                str(self._dict)]
        return "\n".join(lines)

    def optionlist(self):
        """return all known options of the Config object."""
        return sorted(self._dict.keys())
    def get(self, optionname):
        """get an option."""
        return self._dict.get(optionname)
    def set(self, optionname, value):
        """set an option to an arbitrary value."""
        self._dict[optionname]= value
    def env_expand(self, keys):
        r"""expand environment variables in known values.

        All $VARNAME and ${VARNAME} strings are expaned with the values of the
        environment variable VARNAME for the keys in [keys]. If you want to
        keep the dollar '$' sign uninterpreted, precede it with a backslash
        like in '\$VARNAME'.
        """
        dict_= self._dict
        for key in keys:
            val= dict_.get(key)
            if val is None:
                continue
            dict_[key]= sumolib.utils.env_expand(val)
    def _merge(self, dict_):
        """merge known keys from dict_ with self.

        Note: For better backwards compatibility we replace "_" with "-" in all
        keys found in dict_. This means that it is no longer possible that keys
        in a config name *actually* contain "_". So this backwards compability
        hack should be removed in the future.
        """
        for (key, val) in dict_.items():
            # "_" is always replaced with "-". This will be removed in future
            # versions:
            key= key.replace("_","-")
            if not self._dict.has_key(key):
                continue # silently ignore unknown keys
            if isinstance(self._dict[key], list):
                if not isinstance(val, list):
                    raise ValueError("error: config merge: expected a "
                                     "list at %s:%s" % (key,repr(val)))
                self._dict[key].extend(val)
            else:
                self._dict[key]= val
    def _load_file(self, filename, must_exist, enable_loading):
        """load filename.

        Note that the special key "#include" means that another config file is
        included much as with the #include directive in C.
        """
        def _load_lst(dict_, keys):
            """load lists from a dict."""
            l= []
            for k in keys:
                v= dict_.get(k)
                if not v:
                    continue
                l.extend(v)
                del dict_[k]
            return l
        if not os.path.exists(filename):
            if not must_exist:
                return
            raise IOError("error: file \"%s\" doesn't exist" % filename)
        self._real_paths.append(filename)
        data= sumolib.JSON.loadfile(filename)
        # pylint: disable=E1103
        #                     Instance of 'bool' has no 'items' member
        if enable_loading:
            for f in _load_lst(data, ["#include", "#preload"]):
                self._load_file(f, must_exist= True,
                                enable_loading= enable_loading)
            for f in _load_lst(data, ["#opt-preload"]):
                self._load_file(f, must_exist= False,
                                enable_loading= enable_loading)
        self._merge(data)
        if enable_loading:
            for f in _load_lst(data, ["#postload"]):
                self._load_file(f, must_exist= True,
                                enable_loading= enable_loading)
            for f in _load_lst(data, ["#opt-postload"]):
                self._load_file(f, must_exist= False,
                                enable_loading= enable_loading)
    def real_paths(self):
        """return the list of files that should be loaded or were loaded."""
        return self._real_paths
    def load(self, filenames, enable_loading):
        """load from all files in filenames list.

        enable_loading - If True, commands like "#preload" are enabled,
                         otherwise these keys are just treated like ordinary
                         values.
        """
        def unify(l):
            """remove double elements in a list."""
            n= []
            for e in l:
                if e in n:
                    continue
                n.append(e)
            return n
        if filenames:
            for f in filenames:
                if os.path.isfile(f):
                    self._paths.append(f)
        for filename in self._paths:
            self._load_file(filename, must_exist= True,
                            enable_loading= enable_loading)
        # remove double filenames in #preload #postload etc:
        for k in ("#include",
                  "#preload", "#opt-preload",
                  "#postload", "#opt-postload"):
            l= self._dict.get(k)
            if l is None:
                continue
            self._dict[k]= unify(l)

    def save(self, filename, keys, verbose, dry_run):
        """dump in json format"""
        # do not include "None" values:
        dump= {}
        if not keys:
            keys= self._dict.keys()
        for k in keys:
            # we do not distinguish here between items that don't exist
            # and items that have value "None":
            v= self._dict.get(k)
            if v is None:
                continue
            dump[k]= v
        if filename=="-":
            sumolib.JSON.dump(dump)
            return
        backup= sumolib.utils.backup_file(filename, verbose, dry_run)
        if verbose:
            print "creating %s" % filename
        if not dry_run:
            sumolib.JSON.dump_file(filename, dump, backup)

    def merge_options(self, option_obj, merge_opts_set):
        """create from an option object.

        Merge Config object with command line options and
        command line options with Config object.

        All options that are part of the set <merge_opts_set> must be lists.
        For these options the lists are concatenated.
        """
        # pylint: disable=R0912
        #                          Too many branches
        def list_merge(a,b,name):
            """merge two lists."""
            if not isinstance(a, list):
                raise TypeError("error: %s from config file(s) is not "
                                "a list" % name)
            if not isinstance(b, list):
                raise TypeError("error: %s from command line options "
                                "is not a list" % name)
            new= a[:]
            new.extend(b)
            return new

        if merge_opts_set is None:
            merge_opts_set= set()
        else:
            for opt in merge_opts_set:
                if not hasattr(option_obj, opt.replace("-","_")):
                    raise ValueError(
                        "error: '%s' is not a known option" % opt)
        # copy from option_obj to self:
        for opt in self._dict.keys():
            # in the option object, "-" in option names is always
            # replaced with "_":
            oobj_opt= opt.replace("-", "_")
            if not hasattr(option_obj, oobj_opt):
                raise AssertionError(\
                        "ERROR: key '%s' not in the option object" % opt)
            val= getattr(option_obj, oobj_opt)
            if val is not None:
                existing= self._dict.get(opt)
                if existing is None:
                    self._dict[opt]= val
                else:
                    if opt not in merge_opts_set:
                        self._dict[opt]= val
                    else:
                        self._dict[opt]= list_merge(existing, val, opt)

        # copy from self to option_obj:
        for (opt, val) in self._dict.items():
            oobj_opt= opt.replace("-", "_")
            if not hasattr(option_obj, oobj_opt):
                raise AssertionError(\
                        "ERROR: key '%s' not in the option object" % opt)
            if val is not None:
                setattr(option_obj, oobj_opt, val)

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
