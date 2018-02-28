import copy, traceback, threading, re
import simplejson as json

# supposed to be used whenever exception is caught
def attach_tb(e):
    e.__dict__["tb"] = traceback.format_exc()

def is_str(s):
    t = type(s)
    return t == str or t == unicode

class PukalaBaseException(Exception):
    def __init__(self, message, cause):
        Exception.__init__(self, message)
        self.cause = cause
        # tb has message + type inside
        self.tb = None
    def get_desc(self):
        cause = [""]
        if self.cause:
            if hasattr(self.cause, "get_desc"):
                cause = self.cause.get_desc()
            elif hasattr(self.cause, "tb"):
                cause = [self.cause.tb]
            else:
                cause = [str(self.cause)]
        return [self.tb or Exception.__str__(self)] + cause
    def get_formed_desc(self):
        d = self.get_desc()
        return "".join(reversed([i for i in d if i]))

class PukalaStoppedException(PukalaBaseException):
    def __init__(self):
        PukalaBaseException.__init__(self, "stopped", None)


class PukalaGrowException(PukalaBaseException):
    def __init__(self, message, doc, cause=None):
        PukalaBaseException.__init__(self, message, cause)
        self.doc = doc

class PukalaPathException(PukalaBaseException):
    def __init__(self, message, path, cause=None):
        PukalaBaseException.__init__(self, message, cause)
        self.path = path

    def get_desc(self):
        d = PukalaBaseException.get_desc(self)
        return ["path: %s\n" % str(self.path)] + d

class PukalaFCallException(PukalaBaseException):
    def __init__(self, message, fcall, cause=None):
        PukalaBaseException.__init__(self, message, cause)
        self.fcall = fcall

    def get_desc(self):
        d = PukalaBaseException.get_desc(self)
        return ["fcall: %s\n" % str(self.fcall)] + d

class PukalaEvalException(PukalaBaseException):
    def __init__(self, message, path, fcall, cause=None):
        PukalaBaseException.__init__(self, message, cause)
        self.path = path
        self.fcall = fcall

    def get_desc(self):
        d = PukalaBaseException.get_desc(self)
        return ["path: %s\n" % str(self.path),
                "fcall: %s\n" % str(self.fcall)] + d


class CallContext(object):
    def __init__(self, doc, path, args):
        self.doc = doc
        self.path = path
        self.args = args
    def clone(self, args=None):
        res = copy.deepcopy(self)
        if args != None:
            res.args = args
        return res

class FCall(object):
    def __init__(self, fcall):
        if is_str(fcall):
            try:
                fcall = json.loads(fcall)
            except Exception as e:
                attach_tb(e)
                raise PukalaFCallException("expected fcall", fcall, e)
        
        if not fcall[0] == "_fcall":
            raise PukalaFCallException("fcall should start with _fcall", fcall)

        if not len(fcall) > 1:
            raise PukalaFCallException("fcall should be contain at least _fcall and function name", fcall)

        if not is_str(fcall[1]):
            # options present
            if not len(fcall) > 2:
                raise PukalaFCallException("expected fcall function name", fcall)

            if not is_str(fcall[2]):
                raise PukalaFCallException("expected fcall function name is string", fcall)

            if not type(fcall[1]) == dict:
                raise PukalaFCallException("fcall options should be dictionary", fcall)

        self.fcall = copy.deepcopy(fcall)
        self.deps = None

    def get_fcall_str(self):
        return json.dumps(self.fcall)

    def get_fcall_arr(self):
        return self.fcall
        
    def duplicate(self):
        return FCall(self.fcall)

    def add_params(self, *args):
        self.fcall = self.fcall + list(args)

    def get_cgroup(self):
        if (type(self.fcall[1]) == dict and "cgroup" in self.fcall[1]):
            return self.fcall[1]["cgroup"]
        return None

    def do_exec(self, cobj, context, ignore_deps=False):
        if not ignore_deps:
            for i in self.get_deps():
                if not Path.has_path(context.doc, i[1]):
                    raise PukalaFCallException(
                        "dependency %s not fullfilled" % i[0],
                        self.fcall
                    )

        ev_args = []
        for i in self.get_args():
            if FCall.is_fcall_arr(i):
                fcall = FCall(i)
                while True:
                    zz = fcall.do_exec(cobj, context.clone(), True)
                    if not FCall.is_fcall_arr(zz):
                        break                    
                ev_args.append(zz)
            else:
                ev_args.append(i)
        cseg = self.get_fcall_name().split(".")
        while (cseg):
            cobj = getattr(cobj, cseg.pop(0))
        context.args = ev_args
        return cobj(context)

    def get_args(self):
        if type(self.fcall[1]) == dict:
            return self.fcall[3:]
        return self.fcall[2:]

    def get_priority(self):
        if type(self.fcall[1]) == dict and "priority" in self.fcall[1]:
            return self.fcall[1]["priority"]
        return 0

    def get_deps(self):
        if self.deps == None:
            def get_deps2():
                if type(self.fcall[1]) == dict and "deps" in self.fcall[1]:
                    if type(self.fcall[1]["deps"]) != list:
                        self.fcall[1]["deps"] = [self.fcall[1]["deps"]]
                    if self.get_cgroup():
                        raise PukalaFCallException("cgroup is not currently supported for dependent fcalls",
                                                   self.fcall)
                    return [(i, re.compile(i)) for i in self.fcall[1]["deps"]]
                return []
            self.deps = get_deps2()
        return self.deps

    def get_fcall_name(self):
        if type(self.fcall[1]) == dict:
            return self.fcall[2]
        return self.fcall[1]

    @staticmethod
    def is_fcall_arr(fcall):
        return type(fcall) == list and len(fcall) > 0 and fcall[0] == "_fcall"        

    @staticmethod
    def is_fcall_str(fcall):
        return is_str(fcall) and fcall.startswith('["_fcall",')


    @staticmethod
    def extract_fcalls(gdoc, fcall_blocks_traverse=True,
                       is_ignored=None, path_prefixes=("/", [])):
        res = []
        def traverse(doc, path, path_arr):
            if is_ignored(path):
                return
            try:
                if type(doc) == dict:
                    for i in doc:
                        if FCall.is_fcall_str(i):
                            fcall = FCall(i)
                            if is_ignored(fcall=fcall):
                                continue
                            res.append((Path(path_arr + [i]),
                                        fcall))
                            if fcall_blocks_traverse:
                                continue
                        traverse(doc[i], "%s%s/" % (path, i), path_arr + [i])
                elif type(doc) == list:
                    if FCall.is_fcall_arr(doc):
                        fcall = FCall(doc)
                        if not is_ignored(fcall=fcall):
                            res.append((Path(path_arr), fcall))
                    else:
                        index = 0
                        for i in doc:
                            traverse(i, "%s%d/" % (path, index),
                                     path_arr + [index])
                            index += 1
            except PukalaPathException as e:
                raise
            except Exception as e:
                attach_tb(e)
                raise PukalaPathException("couldn't extract fcalls", path, e)
            
        traverse(gdoc, path_prefixes[0], path_prefixes[1])
        return res

    def __str__(self):
        return str(self.fcall)

    def __repr__(self):
        return str(self.fcall)


class Path(object):
    def __init__(self, p, doc=None, abs_path=[]):
        if is_str(p):
            if not doc:
                raise Exception("need doc to create path from string")
            p0 = [i for i in p.split("/") if i]
            if abs_path:
                p0 = self.__resolve(p0, abs_path)

            p = []
            cd = doc
            for i in p0:
                if type(cd) == dict:
                    p.append(i)
                    cd = cd[i]
                elif type(cd) == list:
                    u = int(i)
                    p.append(u)
                    cd = cd[u]
                else:
                    raise PukalaPathException("unknown container type", p)
        self.a_path = copy.copy(p)
        self.s_path = "/".join([str(i) for i in p])
        self.s_path = self.s_path and "/%s/" % self.s_path or "/"
        self.is_key = len(p) and FCall.is_fcall_str(p[-1])
        self.fcall_conf = len(self.a_path) and self.a_path[0] == "_fcall_conf"
        # TODO: check if path is strictly absolute (without . and ..)

    def __resolve(self, rel_path, abs_path):
        p2 = []
        if rel_path and (rel_path[0] == "." or rel_path[0] == ".."):
            p2 = copy.deepcopy(abs_path)
        for i in rel_path:
            if i == ".":
                continue
            if i == "..":
                if not p2:
                    raise PukalaPathException("attempt to get parent of root while resolving", [abs_path, rel_path])
                p2.pop(-1)
            else:
                p2.append(i)
        return p2

    def get_val(self, doc):
        if self.is_key:
            return self.a_path[-1]
        else:
            cd = doc
            for i in self.a_path:
                cd = cd[i]
            return cd

    def check_size(self, size):
        if len(self.a_path) > size:
            raise PukalaPathException("path size exceeded", self)

    def set_val(self, doc, val, strict_keys=True):
        if self.is_key:
            if FCall.is_fcall_arr(val):
                fcall = FCall(val)
                val = fcall.get_fcall_str()
            cd = doc

            for i in self.a_path[:-1]:
                cd = cd[i]
            dk = self.a_path[-1]
            if strict_keys and not val == None and val in cd:
                raise PukalaPathException("duplicate key %s" % str(val), self)
            temp = cd[dk]
            del cd[dk]
            if not val == None:
                cd[val] = temp
        else:
            if FCall.is_fcall_str(val):
                fcall = FCall(val)
                val = fcall.get_fcall_arr()
            cd = doc
            for i in self.a_path[:-1]:
                cd = cd[i]
            cd[self.a_path[-1]] = val

    def get_depth(self):
        return len(self.a_path)

    def as_arr(self):
        return self.a_path

    def as_str(self):
        return self.s_path

    def is_conf_path(self):
        return self.a_path and self.a_path[0] == "_fcall_conf"

    def get_path_repr(self):
        return self.s_path

    def __str__(self):
        return str(self.a_path)

    def __repr__(self):
        return str(self.a_path)

    def duplicate(self):
        return Path(self.a_path)

    def is_fcall_conf(self):
        return self.fcall_conf

    def get_parent(self):
        return Path(self.a_path[:-1])

    def find_subdoc(self, doc):
        cd = doc
        for i in self.a_path:
            cd = cd[i]
        return cd

    def matches(self, regexp):
        return regexp.match(self.s_path)

    @staticmethod
    def has_path(doc, regexp):
        def traverse(doc, path):
            if type(doc) == dict:
                for i in doc:
                    if traverse(doc[i], "%s%s/" % (path, i)):
                        return True
                return False
            elif type(doc) == list:
                index = 0
                for i in doc:
                    if traverse(i, "%s%d/" % (path, index)):
                        return True
                    index += 1
                return False

            else:
                return regexp.match(path) and True or False
        return traverse(doc, "/")


class ContextBase(object):

    def do_lt(self, context):
        if len(context.args) != 2:
            raise Exception("do_lt() requires two arguments")
        return context.args[0] < context.args[1]

    def do_eq(self, context):
        if len(context.args) != 2:
            raise Exception("do_eq() requires two arguments")
        return context.args[0] == context.args[1]

    def do_if(self, context):
        if len(context.args) != 2 and len(context.args) != 3:
            raise Exception("do_if() requires 2-3 arguments")
        if context.args[0] == True:
            return context.args[1]
        if len(context.args) == 3:
            return context.args[2]

    def do_map(self, context):
        if len(context.args) != 2:
            raise Exception("do_map() requires 2 arguments")

        if not FCall.is_fcall_str(context.args[1]):
            raise Exception("do_map() second parameter should be fcall in string form")

        r = context.args[0]
        fc0 = FCall(context.args[1])

        if type(r) == int:
            rr = range(r)
        else:
            rr = r

        ci = 0
        res = []
        for i in rr:
            fc = fc0.duplicate()
            fc.add_params(i, ci)
            ci += 1
            res.append(fc.get_fcall_arr())
        return res

    def do_fmt(self, context):
        if len(context.args) < 1:
            raise Exception("do_fmt() requires at least one argument")
        return str(context.args[0]) % tuple(context.args[1:])

    # TODO: this is workaround to nested calls not being looked for
    # inside arguments; works for lists; more general solution would
    # be necessary
    def ret_args(self, context):
        return context.args

    def do_getsegment(self, context):
        if len(context.args) != 1:
            raise Exception("do_getsegment() requires one argument")
        si = context.args[0]
        return context.path[si]

    def do_getval(self, context):
        if len(context.args) == 0:
            raise Exception("do_getval() requires at least one argument")
        p0 = context.args[0] % tuple(context.args[1:])
        p2 = Path(p0, doc=context.doc,
                  abs_path=context.path.as_arr())
        return p2.get_val(context.doc)

    def do_ret_fcall(self, context):
        if len(context.args) != 1:
            raise Exception("do_ret_fcall() requires one argument")
        fcall = FCall(context.args[0])
        return fcall.get_fcall_arr()

    def do_stop(self, context):
        raise PukalaStoppedException("stopped")

        
class ThreadPool(object):
    def __init__(self, count):
        self.cv = threading.Condition()
        self.tasks = []

        def loop():
            while True:
                task = False
                with self.cv:
                    while True:
                        if self.tasks:
                            if self.tasks[-1] == False:
                                return
                            task = self.tasks.pop(0)
                            break
                        self.cv.wait()
                try:
                    ca, cb = task
                    rr = ca()
                except Exception as e:
                    attach_tb(e)
                    rr = e
                try:
                    cb(rr)
                except Exception as e:
                    # this shouldn't happen; if callback throws
                    # exception, that means calling thread may be
                    # still waiting for tasks to complete; cb
                    # function should do only safe things
                    attach_tb(e)
                    print "fatal exception", str(e.tb)
                    exit(1)
                
        self.threads = []
        for i in range(count):
            t = threading.Thread(target=loop)
            t.daemon = True
            t.start()
            self.threads.append(t)

    # expecting callbacks to not raise exceptions, returning them
    # instead, if that's the case
    def enqueue_tasks(self, tlist, wait_break=True):
        break_occured = [False]
        all_done = threading.Condition()
        def wrap_cb(cb):
            def on_done(res):
                with all_done:
                    zz = cb(res)
                    if zz and not break_occured[0]:
                        break_occured[0] = zz
                        all_done.notify()
            return on_done
        with self.cv:
            if self.tasks and self.tasks[-1] == False:
                raise Exception("shutdown was already initiated")
            if wait_break:
                tlist = [(ca, wrap_cb(cb)) for ca, cb in tlist]
            self.tasks = self.tasks + tlist
            self.cv.notify_all()

        if wait_break:
            with all_done:
                while break_occured[0] == False:
                    all_done.wait(1)
                if isinstance(break_occured[0], Exception):
                    raise break_occured[0]
                return break_occured[0]

    def finish(self):
        with self.cv:
            if self.tasks and self.tasks[-1] == False:
                return
            self.tasks.append(False)
            self.cv.notify_all()
        

def grow(doc, context_obj):
    doc = copy.deepcopy(doc)

    class Conf(object):
        def __init__(self, doc):
            self.doc = doc
            self.defaults = {
                "ignored": [],
                "strict_safe_dict_keys": True,
                "max_depth": 1000,
                # only has meaning for IO operations
                "thread_pool_size": 20,
            }
            self.refresh()
        def refresh(self):
            self.max_depth = self.get_val("max_depth")
            def flatten_list(arr):
                res = []
                def traverse(a):
                    is_fcall = FCall.is_fcall_arr(a)
                    if is_fcall or len(a) and is_str(a[0]):
                        if not is_fcall:
                            res.append(a)
                    else:
                        for i in a:
                            traverse(i)
                traverse(arr)
                return res

            self.ips = {"/_history": True}
            self.ifs = {}
            self.ics = {}
            self.ire = []
            self.iri = []
            if "_fcall_conf" in self.doc and not type(self.doc["_fcall_conf"]) == dict:
                raise Exception("_fcall_conf should be dict")

            if ("_fcall_conf" in self.doc and "thread_pool_size" in
                self.doc["_fcall_conf"]):
                tps = self.doc["_fcall_conf"]["thread_pool_size"]
                if tps < 1:
                    raise PukalaPathException("should be >= 1", "/_fcall_conf/thread_pool_size")

            if ("_fcall_conf" in self.doc and "ignored" in
                self.doc["_fcall_conf"]):
                ig = flatten_list(self.doc["_fcall_conf"]["ignored"])
                if not type(ig) == list:
                    raise PukalaPathException("should be list", "/_fcall_conf/ignored")

                for i in ig:
                    if not type(i) == list and not type(i) == tuple:
                        raise PukalaPathException("ignored item should be list %s" % str(i), "/_fcall_conf/ignored")
                    if len(i) != 2:
                        raise PukalaPathException("ignored item length should be 2 %s" % str(i), "/_fcall_conf/ignored")

                    if i[0] == "path":
                        zz = i[1]
                        if not zz.endswith("/"):
                            zz += "/"
                        self.ips[zz] = True
                    elif i[0] == "function":
                        self.ifs[i[1]] = True
                    elif i[0] == "cgroup":
                        self.ics[i[1]] = True
                    elif i[0] == "regex":
                        self.ire.append(re.compile(i[1]))
                    elif i[0] == "regexi":
                        self.iri.append(re.compile(i[1]))
                    else:
                        raise PukalaPathException("ignored list item should be one of the following: path, function, cgroup %s" % str(i), "/_fcall_conf/ignored")

        def get_val(self, key):
            if "_fcall_conf" in self.doc:
                if key in doc["_fcall_conf"] and not FCall.is_fcall_arr(self.doc["_fcall_conf"][key]):
                    return self.doc["_fcall_conf"][key]
            return self.defaults[key]

        def get_max_depth(self):
            return self.max_depth

        def is_ignored(self, path=None, fcall=None):
            if path:
                if path in self.ips:
                    return True
                for i in self.iri:
                    if not i.match(path):
                        return True
                for i in self.ire:
                    if i.match(path):
                        return True
            if fcall:
                cgroup = fcall.get_cgroup()
                if (fcall.get_fcall_name() in self.ifs or
                        (cgroup and cgroup in self.ics)):
                    return True
            return False

    class History(object):
        def __init__(self, doc, conf):
            self.doc = doc
            self.conf = conf
        def __append_fcall(self, item):
            if not "_history" in self.doc:
                self.doc["_history"] = {}
            if not "fcalls_evaluated" in self.doc["_history"]:
                self.doc["_history"]["fcalls_evaluated"] = []
            self.doc["_history"]["fcalls_evaluated"].append(item)
        def add_call(self, call):
            p, f = call
            self.__append_fcall(["single_call", f.get_fcall_name(), p.as_arr()])
        def add_cgroup(self, calls):
            for i in calls:
                p, f = i
                self.__append_fcall(["cgroup_single", f.get_cgroup(), f.get_fcall_name(), p.as_arr()])

    class FCalls(object):
        def __init__(self, doc, conf, history, context_obj):
            self.doc = doc
            self.history = history
            self.conf = conf
            self.context_obj = context_obj
            self.tpool = ThreadPool(self.conf.get_val("thread_pool_size"))
            self.calls = []
            self.__refresh()
            self.cgroups_done = {}
            self.eval_res_lock = threading.Lock()

        def __refresh(self, paths=None):
            # algorithm is elaborated to avoid full scan of doc
            # tree when extracting fcalls; we traverse only those
            # subtrees which have been evaluated in recent step,
            # according to paths parameter

            # anyway, it is not too optimal and ideally should be
            # rewritten in C; thing is that for small amount of
            # data it doesn't matter
            
            if not paths:
                paths = [Path([])]

            # first step is to prepare paths by extracting them
            # in string format, adding some data for later
            # processing; there are differences for dictionary-key
            # paths and normal paths
            path_candidates = []
            for i in paths:
                offset = 0
                pp = i
                if i.is_key:
                    pp = i.get_parent()
                path_candidates.append((pp.as_str(), pp.as_arr(), pp))

            # group would consist of those paths with single
            # "leader", which is prefix for other parts; we remove
            # all-non leaders from each group (in other words,
            # we don't want to extract fcalls from both parent and
            # child paths, only parent path, as it includes children)
            pc2 = sorted(path_candidates, key=lambda e: e[0])
            pc3 = []
            last_path = None
            for i in pc2:
                if not last_path or not i[0].startswith(last_path):
                    d = i[2].find_subdoc(self.doc)
                    # filtering off those subtrees which obviously
                    # won't have _fcall inside
                    if type(d) == list or type(d) == dict:
                        pc3.append(((i[0], i[1]), d))
                        last_path = i[0]
            subtrees_to_extract = pc3

            # at this point we have nice list of paths; we extract
            # fcalls from each and put all of them in single list
            cs = []
            for ps, d in subtrees_to_extract:
                cs2 = FCall.extract_fcalls(
                    d,
                    is_ignored=conf.is_ignored,
                    path_prefixes=ps
                )
                cs = cs + cs2

            # adding sorting criteria
            def sort_fun(e):
                p, c = e
                if p.is_fcall_conf():
                    depth = 0
                else:
                    depth = p.get_depth()
                return (-c.get_priority(), depth,
                        not p.is_key, p.as_arr(), c.get_cgroup(),
                        c.get_fcall_name())
            cs3 = []
            for p, c in cs:
                cs3.append([p, c, sort_fun((p, c))])

            # joining fcall list with existing fcall list, then
            # sorting, eliminating duplicates (which can be caused
            # by presence of dict key fcalls); checking if any
            # fcall has dependencies as well
            cs4 = sorted(cs3 + self.calls, key=lambda e: e[2])
            has_dependencies = False
            cs5 = []
            last_item = None
            for i in cs4:
                append = True
                if not last_item:
                    append = True
                else:
                    append = i[2] != last_item[2]

                if append:
                    cs5.append(i)
                    if not has_dependencies and i[1].get_deps():
                        has_dependencies = True

            # if there are fcalls with dependencies, doing
            # reordering to ensure fcalls with dependencies are
            # located in the list just after their dependencies
            if has_dependencies:

                # algorithm is as follows
                # 1: each fcall_rec four new fields are added:
                #    - sort criteria #1 (#0 is set by sort_fun())
                #    - dependents
                #    - prev
                #    - next
                # 2: sort criteria #1 is set to [index]
                # 3: dependents are found in n^2 time (worst case)
                # 4: list is traversed single time, using "next";
                #    each step is done for "base" (current)
                #    fcall_rec, creating list of dependents whose
                #    position (according to #0 and #1) is above base,
                #    then sorting this list L (according to #0), then
                #    assigning new #1 for each element so it equals
                #    #1 of the base + [new_index], where new_index
                #    is sequence number of element itself in L.
                # 5: list is ready, just need to nullify prev and
                #    next to help python garbage collector; also, #1
                #    and dependent list has to be thrown away as it
                #    may change when new fcalls are added (#0 is
                #    kept)

                # mutual dependencies cause infinite loop in 4 and
                # are thus detected; ideal solution would be to
                # check if unidirectional graph is acyclic, but to
                # have better performance in general case we just
                # check if number of iterations doesn't exceed n^2;
                # self dependencies are ignored

                # 1, 2
                prev = None
                index = 0
                for i in cs5:
                    i += [[index], [], prev, None]
                    if prev:
                        prev[6] = i
                    prev = i
                    index += 1

                # 3
                for i in cs5:
                    d = i[1].get_deps()
                    if d:
                        for j in cs5:
                            if i[3] == j[3]:
                                # not considering self dependencies
                                continue
                            for k in d:
                                if j[0].matches(k[1]):
                                    j[4].append(i)

                # 4
                curr = cs5 and cs5[0] or None
                iteration = 0
                max_iterations = len(cs5) * len(cs5)
                while curr:
                    if iteration > max_iterations:
                        # TODO: convert to graph and identify
                        # cycle(s) for easier bugfixing
                        raise Exception("mutual dependencies")
                    iteration += 1
                    
                    L = []
                    for i in curr[4]:
                        assert(i[3] != curr[3])
                        if i[3] < curr[3]: 
                            i[3] == curr[3]
                            L.append(i)
                    if L:
                        L = sorted(L, key=lambda e: e[2])
                        ci = 0
                        cc = curr
                        prefix = curr[3]
                        tail = curr[6]
                        for k in L:
                            if k[5]:
                                k[5][6] = k[6]
                            if k[6]:
                                k[6][5] = k[5]
                            k[5] = cc
                            cc[6] = k
                            k[3] = prefix + [ci]
                            ci += 1
                            cc = k
                        if tail:
                            tail[5] = k
                        k[6] = tail
                        
                    curr = curr[6]

                # 5
                curr = cs5 and cs5[0] or None
                while curr and curr[5]: # rolling to first
                    curr = curr[5]
                cs5 = []
                while curr:
                    n = curr[6]
                    curr[5] = None
                    curr[6] = None
                    cs5.append(curr[:3])
                    curr = n
                            
            self.calls = cs5            


        def is_done(self):
            return not len(self.calls)

        def do_exec(self, calls, is_cgroup):
            for p,c in calls:
                p.check_size(self.conf.get_max_depth())
            eval_order = []
            res = []
            def create_call(path, fcall):
                cc = CallContext(
                    copy.deepcopy(self.doc),
                    path,
                    fcall.get_args()
                )
                def do_call():
                    return fcall.do_exec(self.context_obj, cc)
                    
                def cb(r):
                    if isinstance(r, Exception):
                        return PukalaEvalException("couldn't evaluate", path, fcall, r)
                    else:
                        with self.eval_res_lock:
                            eval_order.append((path, fcall))
                            res.append((path, r))
                            if len(res) == len(calls):
                                return True
                return (do_call, cb)

            c2 = [create_call(p.duplicate(), f.duplicate())
                  for p, f in calls]
            self.tpool.enqueue_tasks(c2)
            ssdk = self.conf.get_val("strict_safe_dict_keys")
            with self.eval_res_lock:
                if not is_cgroup:
                    self.history.add_call(calls[0])
                else:
                    self.history.add_cgroup(eval_order)
                for p, r in res:
                    p.set_val(self.doc, r, ssdk)
            
        def evaluate_next(self):
            path, fcall, _ = self.calls.pop(0)
            cgroup = fcall.get_cgroup()
            if cgroup in self.cgroups_done:
                raise PukalaEvalException("partial concurrent group", path, fcall)
                
            refresh_conf = path.is_conf_path()
            if cgroup:
                self.cgroups_done[cgroup] = True
                ci = 0
                calls2 = []
                ccalls = [(path, fcall)]
                for item in self.calls:
                    p2, f2, _ = item
                    if f2.get_cgroup() == cgroup:
                        if (f2.get_priority() !=
                            fcall.get_priority()):
                            raise PukalaEvalException("cgroup member with different priority", path, fcall)
                        ccalls.append((p2, f2))
                        if p2.is_conf_path():
                            refresh_conf = True
                    else:
                        calls2.append(item)
                    ci += 1
                self.calls = calls2
                self.do_exec(ccalls, True)
            else:
                ccalls = [(path, fcall)]
                self.do_exec(ccalls, False)
            if refresh_conf:
                # if configuration was refreshed, rebuilding whole
                # self.calls
                self.conf.refresh()
                self.calls = []
                self.__refresh()
            else:
                self.__refresh([i for i,k in ccalls])

        def finish(self):
            self.tpool.finish()

    fcalls = None
    
    try:
        conf = Conf(doc)
        history = History(doc, conf)
        fcalls = FCalls(doc, conf, history, context_obj)
        while not fcalls.is_done():
            fcalls.evaluate_next()
        fcalls.finish()
        return doc
    except (KeyboardInterrupt, Exception) as e:
        if fcalls:
            fcalls.finish()
        attach_tb(e)
        raise PukalaGrowException("tree growing failed", doc, e)

