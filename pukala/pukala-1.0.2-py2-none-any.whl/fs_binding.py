import re, os, os.path, yaml, shutil, subprocess
import simplejson as json

import xml.etree.ElementTree as ET
from pukala import FCall, Path, PukalaBaseException

class PukalaFsException(PukalaBaseException):
    def __init__(self, cmd, cwd, retcode, out, err, cause=None):
        PukalaBaseException.__init__(self, "command execution failed", cause)
        self.cmd = cmd
        self.cwd = cwd
        self.retcode = retcode
        self.out = out
        self.err = err

    def get_desc(self):
        d = PukalaBaseException.get_desc(self)
        return [
            "err: %s\n" % str(self.err),
            "out: %s\n" % str(self.out),
            "retcode: %d\n" % self.retcode,
            "cwd: %s\n" % str(self.cwd),
            "cmd: %s\n" % str(self.cmd),
        ] + d


class FsBinding(object):

    def __init__(self, prefix="", root_cobj=None):
        self.prefix = prefix
        self.re_cache = {}
        self.root_cobj = root_cobj and root_cobj or self

    def get_ftypes(self, context):
        return [
            ["^file://.*~$", "ignored"],
            ["^file://.*\\.txt$", "text"],
            ["^file://.*\\.cfg$", "text"],
            ["^file://.*\\.yml$", "yaml"],
            ["^file://.*\\.yaml$", "yaml"],
            ["^file://.*\\.json$", "json"],
            ["^file://.*\\.xml$", "xml"],
            ["^file://.*$", "closed_file"],
            ["^folder://.*$", "closed_folder"],
        ]

    def get_handlers(self, context):
        def do_format(r):
            res = {}
            for k,v in r.iteritems():
                res[k] = [json.dumps(["_fcall", "%s%s" %
                                      (self.prefix, i.__name__)])
                          for i in v]
            return res
        res = {
            "ignored": [self.pull_ignored, self.push_ignored],
            "text": [self.pull_text, self.push_text],
            "yaml": [self.pull_yaml, self.push_yaml],
            "json": [self.pull_json, self.push_json],
            "xml": [self.pull_xml, self.push_xml],
            "closed_file": [self.pull_closed_file,
                            self.push_closed_file],
            "closed_folder": [self.pull_closed_folder,
                              self.push_closed_folder],
            "open_folder": [self.pull_open_folder,
                            self.push_open_folder]
        }
        return do_format(res)

    def get_defaults(self, context):
        return {
            "ftypes": self.get_ftypes(context),
            "handlers": self.get_handlers(context),
        }

    def push_ignored(self, context):
        return None
        
    def push_text(self, context):
        source = context.args[0]
        target_path = context.args[1]
        with open(target_path, "w") as f:
            f.write("\n".join(source["contents"]))
        
    def push_yaml(self, context):
        source = context.args[0]
        target_path = context.args[1]
        with open(target_path, "w") as f:
            f.write(yaml.dump(source["contents"]))

    def push_json(self, context):
        source = context.args[0]
        target_path = context.args[1]
        with open(target_path, "w") as f:
            f.write(json.dumps(source["contents"]))

    def push_xml(self, context):
        source = context.args[0]
        target_path = context.args[1]
        def unparse_tree(e):
            if type(e) == str:
                return e
            contents = "".join([unparse_tree(i) for i in e["c"]])
            attribs = " ".join(['%s="%s"' % (k, v) for k,v in e["a"].iteritems()])
            if attribs:
                attribs = " " + attribs
            d = {
                "tag": e["_t"],
                "attribs": attribs,
                "contents": contents
            }
            return "<%(tag)s%(attribs)s>%(contents)s</%(tag)s>" % d
        with open(target_path, "w") as f:
            f.write(unparse_tree(source["contents"]))

    def push_closed_file(self, context):
        source = context.args[0]
        target_path = context.args[1]
        shutil.copyfile(source["path"], target_path)

    def push_closed_folder(self, context):
        source = context.args[0]
        target_path = context.args[1]
        if os.path.exists(target_path):
            raise Exception("path exists %s" % target_path)
        shutil.copytree(source["path"], target_path)

    def push_open_folder(self, context):
        source = context.args[0]
        target_path = context.args[1]
        cfg = context.args[2]
        source_path = context.args[3]
        if os.path.exists(target_path):
            raise Exception("path exists %s" % target_path)
        os.makedirs(target_path)
        for k,v in source["contents"].iteritems():
            tp2 = os.path.join(target_path, k)
            p = Path(source_path, context.doc, context.path.as_arr())
            p2 = Path(p.as_arr() + ["contents", k])
            c2 = context.clone()
            c2.args = [p2.as_arr(), tp2, cfg]
            self.save_inode(c2)

    def pull_ignored(self, context):
        return None
        
    def pull_text(self, context):
        path = context.args[0]
        with open(path, "r") as f:
            data = f.read()

        res = []
        for i in data.split("\n"):
            if FCall.is_fcall_str(i):
                fcall = FCall(i)
                res.append(fcall.get_fcall_arr())
            else:
                res.append(i)
        return {
            "contents": res
        }

    def pull_yaml(self, context):
        path = context.args[0]
        with open(path, "r") as f:
            return {
                "contents": yaml.load(f.read())
            }
    def pull_json(self, context):
        path = context.args[0]
        with open(path, "r") as f:
            return {
                "contents": json.loads(f.read())
            }
            
    def pull_xml(self, context):
        # TODO: elemtree offers only limited support for parsing
        # xml declaration tag (<?xml ...?>); probably need to use
        # lxml (also comments are not supported; and namespaces
        # are omitted as well)
        path = context.args[0]
        tree = ET.parse(path)
        root = tree.getroot()
        def parse_tree(t):
            contents = []
            if t.text and t.text.strip():
                contents.append(t.text.strip())
            for i in t:
                contents.append(parse_tree(i))
                if i.tail and i.tail.strip():
                    contents.append(i.tail.strip())
            return {
                "_t": t.tag,
                "a": t.attrib,
                "c": contents
            }
        return {
            "contents": parse_tree(root)
        }

    def pull_closed_file(self, context):
        path = context.args[0]
        return {
            "path": path
        }
    def pull_closed_folder(self, context):
        path = context.args[0]
        return {
            "path": path
        }
    def pull_open_folder(self, context):
        path = context.args[0]
        res = {}
        for i in os.listdir(path):
            context.args[0] = os.path.join(path, i)
            res[i] = self.open_inode(context)
        return {
            "contents": res
        }

    def open_inode(self, context):
        def is_match(p, path2):
            if not p in self.re_cache:
                self.re_cache[p] = re.compile(p)
            return self.re_cache[p].match(path2)
        path = context.args[0]
        cfg = context.args[1]
        if type(cfg) == str:
            p = Path(cfg, context.doc)
            cfg = p.get_val(context.doc)

        if not os.path.exists(path):
            raise Exception("path doesn't exist %s" % path)
        gtype = os.path.isfile(path) and "file" or "folder"
        path2 = "%s://%s" % (gtype, path)
        ftype = None

        for p,ft in cfg["ftypes"]:
            if is_match(p, path2):
                ftype = ft
                break

        if not ftype:
            raise Exception("undefined type for %s" % path2)
                
        if not ftype in cfg["handlers"]:
            raise Exception("unknown type for %s, %s" % (path2,
                                                         ftype))
        fcall = FCall(cfg["handlers"][ftype][0])
        fcall.add_params(path, cfg)
        res = fcall.do_exec(self.root_cobj, context.clone())
        if res:
            res["ftype"] = ftype
            if cfg.get("add_path", False):
                res["path"] = path
        return res

    def save_inode(self, context):
        source_path = context.args[0]
        target_path = context.args[1]
        cfg = context.args[2]
        if type(cfg) == str:
            p = Path(cfg, context.doc)
            cfg = p.get_val(context.doc)

        tp = Path(source_path, context.doc, context.path.as_arr())
        inode = tp.get_val(context.doc)
        if not inode:
            return
        if not "ftype" in inode:
            raise Exception("undefined type for %s" % source_path)
            
        ftype = inode["ftype"]
        if not ftype in cfg["handlers"]:
            raise Exception("unknown type for %s, %s" % (source_path,
                                                         ftype))
        
        fcall = FCall(cfg["handlers"][ftype][1])
        fcall.add_params(inode, target_path, cfg, source_path)
        return fcall.do_exec(self.root_cobj, context.clone())

    def exec_local(self, context):
        cmd = context.args[0]
        opts = len(context.args) > 1 and context.args[1] or {}
        cwd = opts.get("cwd", None)
        if (len(cmd) >= 3 and cmd[0] == "rm" and
            ("-rf" in cmd or "-r" in cmd)
            and "*" in "".join(cmd) and
            not "allow_rm_rf_asterisk" in opts):
            raise Exception("wildcard * not allowed with rm -r, use allow_rm_rf_asterisk in opts dictionary to bypass this check")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd)
        # TODO: support output for long-running things would be cool
        out, err = p.communicate()
        if p.returncode:
            raise PukalaFsException(cmd, cwd, p.returncode, out, err)
        out = out and out or ""
        err = err and err or ""
        out = out.split("\n")
        err = err.split("\n")
        return {
            "cmd": cmd,
            "cwd": cwd,
            "out": out,
            "err": err
        }
            
    def send_file(self, context):
        (a_file, cert_file, username, host,
         target_folder) = context.args

        cmd = ['scp', '-oStrictHostKeyChecking=no', '-i', cert_file,
               a_file, "%s@%s:%s" % (username, host, target_folder)]
        return self.exec_local(context.clone([cmd]))

    def get_file(self, context):
        (a_file, cert_file, username, host,
         target_folder) = context.args

        cmd = ['scp', '-oStrictHostKeyChecking=no', '-i', cert_file,
               "%s@%s:%s" % (username, host, a_file), target_folder]
        return self.exec_local(context.clone([cmd]))

    def exec_remote(self, context):
        cert_file, username, host, cmd0 = context.args
        cmd = ['ssh', '-i', cert_file, "%s@%s" % (username, host),
               cmd0]
        return self.exec_local(context.clone([cmd]))
        
        

