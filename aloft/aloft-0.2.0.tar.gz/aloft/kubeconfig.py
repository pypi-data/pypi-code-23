import os
from aloft.output import print_action


class kubeconfig(object):

    def __init__(self, kubeconfig_filename):
        print_action(f'Using kubeconfig {kubeconfig_filename}')
        self.temporary_kubeconfig_filename = kubeconfig_filename

    def __enter__(self):
        self.original_kubeconfig = self.set_kubeconfig(self.temporary_kubeconfig_filename)
        return self.temporary_kubeconfig_filename

    def __exit__(self, type, value, traceback):
        self.set_kubeconfig(self.original_kubeconfig)

    @staticmethod
    def set_kubeconfig(kubeconfig_filename):
        original_kubeconfig = os.environ.get('KUBECONFIG', None)

        if kubeconfig_filename:
            os.environ['KUBECONFIG'] = kubeconfig_filename
        else:
            del os.environ['KUBECONFIG']

        return original_kubeconfig
