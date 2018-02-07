# -*- coding: utf-8 -*-
import click
from .base import BaseCommand, argument, option, types, register  # noqa
from modelhub.core.models import Model


@register("export")
class Command(BaseCommand):
    arguments = [
        argument("model_name"),
        argument("output_path", type=click.Path()),
        option("-f", "--format", default="GraphDef", type=click.Choice(["GraphDef", "MetaGraphDef", "FreezeGraphDef"])),
        # option("-s", "--signature_def", default="serving_default"),
        option("--tag", default="serve"),
        option("-t", "--text", is_flag=True)
    ]

    def run(self, model_name, output_path, format, tag, text):
        "export tensorflow saved_model with format"
        model_name, version = Model.split_name_version(model_name)
        model = Model.get_local(model_name)
        model_version = model.get_version(version)

        from modelhub.utils.convert_freeze_graph import freeze_model, get_meta_graph_def
        meta_graph_def = get_meta_graph_def(model_version.saved_model_def, tag)

        if format == "MetaGraphDef":
            return self.save_pb(meta_graph_def, output_path, text)

        if format == "FreezeGraphDef":
            return self.save_pb(freeze_model(meta_graph_def, model_version.local_path), output_path, text)
        graph_def = meta_graph_def.graph_def
        if format == "GraphDef":
            return self.save_pb(graph_def, output_path, text)
        raise ValueError("Unsupport format %s" % format)

    def save_pb(self, pb, output_path, text):
        if text:
            with open(output_path, "w") as f:
                f.write(repr(pb))
        else:
            with open(output_path, "wb") as f:
                f.write(pb.SerializeToString())
