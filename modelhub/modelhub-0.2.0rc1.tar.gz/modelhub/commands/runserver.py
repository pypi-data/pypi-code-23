# -*- coding: utf-8 -*-
import click
from .base import BaseCommand, argument, option, types, register  # noqa
from modelhub.core.models import Model
from modelhub.core.utils import cached_property


@register("runserver")
class Command(BaseCommand):
    arguments = [
        argument("models_name", nargs=-1),
        option("-b", "--bin_path", type=click.Path(exists=True)),
    ]

    bin_path = "/usr/bin/tensorflow_model_server"

    @cached_property
    def bin_path(self):
        import subprocess
        return subprocess.check_output(["which", "tensorflow_model_server"]).strip().decode()

    def run(self, models_name, bin_path=None):
        """run tensorflow_model_server with models"""
        if not models_name:
            return

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

    def _run_server(self, model_config_file, port=8500, **kwargs):
        from subprocess import Popen
        Popen([
            self.bin_path,
            "--port=%s" % port,
            "--model_config_file=%s" % model_config_file
        ] + [
            "--%s=%s" % (key, value) for key, value in kwargs.items()
        ]).wait()
