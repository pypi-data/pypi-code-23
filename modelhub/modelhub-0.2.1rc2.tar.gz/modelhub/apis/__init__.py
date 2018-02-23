# -*- coding: utf-8 -*-
from modelhub.core import models


def get_model_path(model_name, version=None, ensure_newest_version=False):
    if version:
        model = models.Model.get_local(model_name)
        version = model.get_version(version)
    else:
        if ensure_newest_version:
            model = models.Model.get(model_name)
            version = model.latest_version
        else:
            model = models.Model.get_local(model_name)
            for version in reversed(model.versions):
                if version.local_exists:
                    break
            else:
                version = model.latest_version

    if not version.local_exists:
        version.checkout()
    return version.local_path
