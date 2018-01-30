import re
import six

zpaths = {
    "bt": "android.widget.Button",
    "cb": "android.widget.CheckBox",
    "el": "android.widget.ExpandableListView",
    "et": "android.widget.EditText",
    "fl": "android.widget.FrameLayout",
    "gl": "android.widget.GridLayout",
    "gv": "android.widget.GridView",
    "h":  "hierarchy",
    "ib": "android.widget.ImageButton",
    "iv": "android.widget.ImageView",
    "ll": "android.widget.LinearLayout",
    "lv": "android.widget.ListView",
    "rl": "android.widget.RelativeLayout",
    "rv": "android.support.v7.widget.RecyclerView",
    "sp": "android.support.v4.widget.SlidingPaneLayout",
    "sv": "android.widget.ScrollView",
    "th": "android.widget.TabHost",
    "tl": "android.widget.TableLayout",
    "tr": "android.widget.TableRow",
    "tv": "android.widget.TextView",
    "tw": "android.widget.TabWidget",
    "v":  "android.view.View",
    "vg": "android.view.ViewGroup",
    "vp": "android.support.v4.view.ViewPager"
}


def create_zpath_tags():
    global zpath_tags
    if six.PY3:
        return dict((v, k) for k, v in zpaths.items())
    else:
        return dict((v, k) for k, v in zpaths.iteritems())


zpath_tags = create_zpath_tags()


def replace_zpaths(new_zpaths):
    global zpaths, zpath_tags
    zpaths = new_zpaths
    zpath_tags = create_zpath_tags()


def set_zpath_tag(abbreviation, zpath):
    global zpaths, zpath_tags
    zpaths[abbreviation] = zpath
    zpath_tags = create_zpath_tags()


def get_zpath_tag(path):
    if path in zpath_tags:
        return zpath_tags[path]
    else:
        return path


re_elem_index = re.compile('([^\[\]]*)(\[[^\]]+\])?')

re_tokens = re.compile(r'\b[a-z]{1,3}\b')


def expand_zpath(zpath):
    other = re_tokens.split(zpath)
    tokens = re_tokens.findall(zpath)
    new_zpath = ''
    while len(other) or len(tokens):
        if len(other):
            new_zpath += other.pop(0)
        if len(tokens):
            abbrev = tokens.pop(0)
            if abbrev in zpaths:
                new_zpath += zpaths[abbrev]
            else:
                new_zpath += abbrev
    return new_zpath


