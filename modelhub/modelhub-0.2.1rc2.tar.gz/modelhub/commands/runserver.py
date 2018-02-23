# -*- coding: utf-8 -*-
import click
import os
from .base import BaseCommand, argument, option, types, register  # noqa
from modelhub.core.models import Model
from modelhub.core.utils import cached_property

# TODO: move to config
REDIS_URL_ENV_KEY = "RD_REDIS_URL"
REDIS_PREFIX_ENV_KEY = "RD_REDIS_PREFIX"
REDIS_TIMEOUT = 10


@register("runserver")
class Command(BaseCommand):
    arguments = [
        argument("models_name", nargs=-1),
        option("-b", "--bin_path", type=click.Path(exists=True)),
        option("-r", "--register_model", is_flag=True)
    ]

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.redis_url = os.getenv(REDIS_URL_ENV_KEY)
        self.redis_prefix = os.getenv(REDIS_PREFIX_ENV_KEY, "")
        # bin_path = "/usr/bin/tensorflow_model_server"

    @cached_property
    def bin_path(self):
        import subprocess
        return subprocess.check_output(["which", "tensorflow_model_server"]).strip().decode()

    def run(self, models_name, bin_path=None, register_model=False):
        """run tensorflow_model_server with models"""
        if not models_name:
            self.echo("no model name provided")
            return

        self.is_register_model = register_model

        if bin_path:
            self.bin_path = bin_path

        models = [Model.get_local(model_name) for model_name in models_name]

        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile("r+") as f:
            f.write(self.generate_model_config(models))
            f.flush()
            self.echo("server bin_path:\t%s" % self.bin_path)
            self.echo("model_config_file:\t%s" % f.name)
            self._run_server(
                models=models,
                model_config_file=f.name,
            )

    def generate_model_config(self, models):
        from tensorflow_serving.config.model_server_config_pb2 import ModelServerConfig, ModelConfigList, ModelConfig

        def build_model_config(model):
            assert model.latest_local_version.manifest.is_saved_model, "%s is not a TensorFlow Model, cannot serving" % model.name
            return ModelConfig(
                name=model.name,
                base_path=model.local_path,
                model_platform="tensorflow"
            )

        res = str(ModelServerConfig(
            model_config_list=ModelConfigList(
                config=[build_model_config(model) for model in models]
            )
        ))
        # print(res)
        return res

    auto_discovery = None

    def _register_model(self, models, port):
        if not self.auto_discovery:
            from modelhub.tf_serving import AutoDiscovery, parse_redis_url, get_local_ip
            self.hostport = "%s:%d" % (get_local_ip(), port)
            if not self.redis_url:
                raise ValueError("No REDIS url configured, should set env '%s'" % REDIS_URL_ENV_KEY)
            ad_args = parse_redis_url(self.redis_url)
            ad_args["redis_prefix"] = self.redis_prefix
            self.auto_discovery = AutoDiscovery(**ad_args)
        for model in models:
            print("register", model.name)
            self.auto_discovery.register(
                model.name,
                model.latest_local_version.manifest.seq,
                self.hostport
            )

    def _run_server(self, models, model_config_file, port=8500, **kwargs):
        from subprocess import Popen, PIPE, TimeoutExpired
        popen = Popen(
            [
                self.bin_path,
                "--port=%s" % port,
                "--model_config_file=%s" % model_config_file
            ] + [
                "--%s=%s" % (key, value) for key, value in kwargs.items()
            ],
            stdin=PIPE,
            stderr=PIPE if self.is_register_model else None
        )
        try:
            if not self.is_register_model:
                return popen.wait()
            # initialized = False
            while True:
                line = popen.stderr.readline().decode()
                print(line, end="")
                if "Running ModelServer at" in line:
                    # initialized = True
                    self._register_model(models, port)
                    break

            while True:
                try:
                    popen.wait(timeout=REDIS_TIMEOUT)
                    # print("out", stderr)
                except TimeoutExpired:
                    self._register_model(models, port)
        finally:
            print("Killing")
            popen.kill()
