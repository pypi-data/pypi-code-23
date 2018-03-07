import datetime
import os

from .modules import modules
from .yaml import yaml, Loader, Dumper


class Steroids:
    input_file = None
    output_file = None

    def __init__(self, **kwargs):
        self.path = kwargs.get('path')
        self.input_file = kwargs.get('input_file')
        self.output_file = kwargs.get('output_file')
        self.modules = [module(**kwargs) for module in modules]
        super().__init__()
        self.compose = self.read()

    def read(self, path=None):
        if path is None:
            path = os.path.join(self.path, self.input_file)
        with open(path) as f:
            return yaml.load(
                f.read(),
                Loader=Loader,
            )

    def write(self, path=None):
        if path is None:
            path = os.path.join(self.path, self.output_file)
        with open(path, 'w') as f:
            msg = "# Generated on {:%Y-%m-%d %H:%M}\n"
            now = datetime.datetime.utcnow()
            f.write(msg.format(now))
            yaml.dump(
                self.compose,
                f,
                Dumper=Dumper,
                default_flow_style=False,
            )

    def inject(self):
        for module in self.modules:
            module.run(self.compose)
        self.write()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        help='Path to stack directory',
    )
    parser.add_argument(
        '--persist-prefix',
        help='Path to local-persist storage',
    )
    parser.add_argument(
        '--input-file',
        default='compose.steroids.yml',
        help='Input file name',
    )
    parser.add_argument(
        '--output-file',
        default='compose.generated.yml',
        help='Output file name',
    )
    parser.add_argument(
        '--lb-net',
        dest='loadbalancer_network',
    )
    args = vars(parser.parse_args())
    Steroids(
        **args,
    ).inject()
