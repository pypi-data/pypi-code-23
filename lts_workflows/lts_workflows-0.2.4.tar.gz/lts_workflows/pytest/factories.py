#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import yaml


def snakemake_core_setup(snakefile, config=None, **kwargs):
    @pytest.fixture(scope=kwargs.get("scope", "function"),
                    autouse=kwargs.get("autouse", False))
    def snakemake_list(request, tmpdir_factory):
        p = tmpdir_factory.mktemp("snakemakelist")
        p.join(kwargs.get("snakefile_name",
                          "Snakefile")).mksymlinkto(snakefile)
        if not kwargs.get("sampleinfo", None) is None:
            p.join("sampleinfo.csv").mksymlinkto(kwargs["sampleinfo"])
        if config is not None:
            p.join("config.yaml").mksymlinkto(config)
            with p.join("config.fmt.yaml").open("w") as fh:
                fh.write(yaml.dump({'settings':
                                    {'runfmt': '',
                                     'samplefmt': ''}},
                                   default_flow_style=False))
        return p
    return snakemake_list
