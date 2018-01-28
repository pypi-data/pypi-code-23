import os.path
import random
import re
from untei from constants.Const

def user_input_yes_or_no(ans):
    if ans.lower() in [ "yes", "y", "yeah", "yep", "yup" ]:
        return True
    elif ans.lower() in [ "no", "n", "nope" ]:
        return False
    else:
        return None

def is_uncopied(filename):
    if filename in ["site_config.txt", "template.html", "__pycache__"] :
        return True
    elif re.fullmatch(".*[.]pyc{0,1}", filename):
        return True
    else:
        return False

def safe_apply_template(template, assignment_dict):
    safe_assignment_dict = {}
    for check_key in assignment_dict.keys():
        for key in assignment_dict.keys():
            if key in assignment_dict[check_key]:
                # create a temporary key
                while True:
                    temp_key = str(random.random())
                    if not(temp_key in assignment_dict[key]) and not(temp_key in template):
                        break

                # Evacuation
                safe_assignment_dict[temp_key] = key
                assignment_dict[check_key] = assignment_dict[check_key].replace(key, temp_key)
            else:
                pass
    rep = replace_with_dict(template, assignment_dict)
    rep = replace_with_dict(rep, safe_assignment_dict)
    return rep


def replace_with_dict(target, assignment_dict):
    rep = target
    for key in assignment_dict.keys():
        rep = rep.replace(key, assignment_dict[key])
    return rep


def order_articles_by_date(articles):
    n = len(articles)
    if n <= 1:
        return articles

    pivot_date = articles[int(0.5 * n)].date

    later   = []
    earlier = []

    for a in articles:
        if a.date >= pivot_date:
            later.append(a)
        else:
            earlier.append(a)

    if len(later) <= 1 or len(earlier) <= 1:
        later.extend(earlier)
        return later
    else:
        earlier = order_articles_by_date(earlier)
        later   = order_articles_by_date(later)
        later.extend(earlier)
        return later

def file_type(file_name):
    root, ext = os.path.splitext(file_name)
    if ext in Const.EXTENSIONS_FOR_MARKDOWN:
        return Const.FILE_TYPE_MARKDOWN
    elif ext in Const.EXTENSIONS_FOR_HTML:
        return Const.FILE_TYPE_HTML
    elif ext == "":
        return Const.FILE_TYPE_DIRECTORY
    else:
        print("Warn: Find an extension out of scope: ", ext)
        return ext

def file_name(path):
    return os.path.basename(path).split(".")[0]


def does_include_template_variables(s):
    rtn = False
    for var in Const.TEMPLATE_VARIABLES:
        rtn = rtn or (var in s)

    return rtn

def handled_files():
    return [f for f in os.listdir(Const.FILES_PATH) if file_type(f) != Const.FILE_TYPE_DIRECTORY]
