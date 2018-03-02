import xyxy.config
import importlib.util
from pathlib import Path
import requests
import os
import json
from datetime import datetime


def get_formula_path(formula_name):
    return Path(xyxy.config.xyxy_home_dir).expanduser() / formula_name / "{}.py".format(formula_name)


def download_formula(formula_name):
    url = xyxy.config.xyxy_formulas_url + '{}.py'.format(formula_name)
    destination = get_formula_path(formula_name)
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    r = requests.get(url)
    r.raise_for_status()
    if r.status_code == 200:
        data = r.content
        with open(destination, 'wb') as f:
            f.write(data)


def load_formula(formula_name):
    path = get_formula_path(formula_name)
    spec = importlib.util.spec_from_file_location("Formula", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, formula_name.capitalize())()


def use_cache(formula_name):
    # TODO: rename function
    cache_path = Path(xyxy.config.xyxy_home_dir).expanduser() / xyxy.config.cache_filename
    if not os.path.exists(cache_path):
        return False

    with open(cache_path, 'r+') as f:
        try:
            data = json.load(f)
        except:
            return False

    last_revision = data.get(formula_name)

    if last_revision is not None:
        try:
            last_revision = datetime.strptime(
                last_revision, "%Y-%m-%d %H:%M:%S")
            return (datetime.now() - last_revision).days < 1
        except:
            return False
    else:
        return False


def update_cache(formula_name, delete=False):
    cache_path = Path(xyxy.config.xyxy_home_dir).expanduser() / xyxy.config.cache_filename

    with open(cache_path, 'w') as f:
        try:
            data = json.load(f)
        except:
            data = {}

        if delete:
            data.pop(formula_name, None)
        else:
            data[formula_name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        json.dump(data, f)


class ValidationError(Exception):
    def __init__(self, message, errors):
        super(ValidationError, self).__init__(message)


def load(formula_name):
    path = get_formula_path(formula_name)

    if not path.is_file() or not use_cache(formula_name):
        download_formula(formula_name)
        update_cache(formula_name)

    formula = load_formula(formula_name)

    return use(formula)


def use(formula):
    if not formula.is_downloaded():
        formula.download()

    try:
        formula.validate()
    except:
        formula.clear()
        update_cache(formula.name, delete=True)
        raise ValidationError("Validation failed")

    return formula.load()
