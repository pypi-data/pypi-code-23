import os.path

from catabrowse.irodscatalog import iRODSCatalog, make_irods3_catalog

from irods.models import DataObject, Collection
from irods.exception import *

from six import print_

ic = make_irods3_catalog('/home/pigay/.irods/.irodsEnv')

print_(ic)
print_(ic.dom)
print_(ic.cm)

coll = ic.session.collections.get('/MCIA/home/pigay/testdir')

print_(coll)
print_(coll.path)
print_(coll.metadata.keys())

q = ic.session.query(DataObject.name, DataObject.owner_name, DataObject.size, DataObject.modify_time).filter(Collection.id == coll.id)

#for r in q.all():
#    print_(r)

print_('coucou')
q = ic.session.query(DataObject.name, DataObject.owner_name, DataObject.size, DataObject.modify_time, Collection.name).filter(Collection.name == coll.path).filter(DataObject.name == 'unison.log')
for r in q.all():
    print_(r)

print_(ic.lstat('/MCIA/home/pigay/testdir/unison.log'))

print_(ic.listdir('/MCIA/home/pigay/testdir'))
print_(ic.isdir('/MCIA/home/pigay/testdir'))
print_(ic.isdir('/MCIA/home/pigay/testdir/unison.log'))

print_(ic.join('a', 'b', 'c'))

ic.download_files(['/MCIA/home/pigay/testdir/unison.log'], '/tmp')

testcoll = '/MCIA/home/pigay/testdir/testcatabrowse'

try:
    ic.mkdir(testcoll)
except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
    print_('collection already present. mkdir not tested')

ic.upload_files([os.path.abspath('catabrowse.geany'), os.path.abspath('.gitignore')], testcoll)

ic.download_files([ic.join(testcoll, 'catabrowse.geany'), ic.join(testcoll, '.gitignore')], '/tmp')

ic.delete_files([ic.join(testcoll, '.gitignore'), ])


ic.upload_directories([os.path.abspath('catabrowse')], testcoll)

ic.download_directories([ic.join(testcoll, 'catabrowse'), ], '/tmp')

ic.delete_directories([ic.join(testcoll, 'catabrowse'), ])
