import os

from serverfiles import LocalFiles, ServerFiles

from Orange.data import Table
from Orange.misc.environ import data_dir


server_url = "http://butler.fri.uni-lj.si/datasets/"
PATH = os.path.join(data_dir(), "datasets")
localfiles = LocalFiles(PATH, serverfiles=ServerFiles(server=server_url))


def load(name):
    return Table(name)


if __name__ == '__main__':
    print(localfiles.serverfiles.allinfo())
    #localfiles.download()
    print('vsi:', localfiles.serverfiles.listfiles())
    print('lokalni:', localfiles.listfiles())
    #path = localfiles.localpath_download('core', 'iris.tab')
    #print(path)

