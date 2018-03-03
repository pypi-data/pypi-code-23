import pygsti
import numpy as np
import pickle


def assertArraysAlmostEqual(a,b):
    assert(np.linalg.norm(a-b) < 1e-6)

ds = pygsti.objects.DataSet() #outcomeLabels=['0','1'])

ds.add_count_dict( ('Gx',), {'0': 10, '1': 90} )

ds[ ('Gx',) ] = {'0': 10, '1': 90}
ds[ ('Gx',) ]['0'] = 10
ds[ ('Gx',) ]['1'] = 90
ds[ ('Gy',) ] = {'0': 20, '1': 80}
ds[ ('Gx','Gy') ] = {('0','0'): 30, ('1','1'): 70}

ds.done_adding_data()
print(ds)

dsWritable = ds.copy_nonstatic()
dsWritable[('Gy',)] = {'0': 20, '1': 80}

ds_str = str(ds)

print(ds[('Gx',)]['0']) #, 10)
print(ds[('Gx',)].fraction('0')) #, 0.1)

#Pickle and unpickle
with open('testDataset.pickle', 'wb') as datasetfile:
    pickle.dump(ds, datasetfile)

ds_from_pkl = None
with open('testDataset.pickle', 'rb') as datasetfile:
    ds_from_pkl = pickle.load(datasetfile)

print(ds_from_pkl)

ordering = [('0',), ('1',), ('0','0'), ('1','1')]
pygsti.io.write_dataset("testDataset1.txt", ds, outcomeLabelOrder=None, fixedColumnMode=True)
pygsti.io.write_dataset("testDataset2.txt", ds, outcomeLabelOrder=None, fixedColumnMode=False)
pygsti.io.write_dataset("testDataset1.txt", ds, outcomeLabelOrder=ordering, fixedColumnMode=True)
pygsti.io.write_dataset("testDataset2.txt", ds, outcomeLabelOrder=ordering, fixedColumnMode=False)


ds1 = pygsti.io.load_dataset("testDataset1.txt")
ds2 = pygsti.io.load_dataset("testDataset2.txt")

print("\nDS1:"); print(ds1)
print("\nDS2:"); print(ds2)

print("DONE")
