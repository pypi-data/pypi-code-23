import xyxy.config
import importlib.util
from pathlib import Path
import requests
import os


def get_formula_path(formula_name):
    return Path(xyxy.config.xyxy_base_path).expanduser() / formula_name / "{}.py".format(formula_name)


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


def load(formula_name, use_cache=True):
    path = get_formula_path(formula_name)

    if not path.is_file() or not use_cache:
        download_formula(formula_name)

    formula = load_formula(formula_name)

    if not formula.is_downloaded():
        formula.download_dataset()

    return formula.load_data()
