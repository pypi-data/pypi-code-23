import h5py as h5
import numpy as np

class Label:
    """
    Structure to store label data, just wraping numpy arrays
    """
    def __init__(self):
        self.events = np.zeros((0,3),dtype=np.uint32)
        self.status = np.zeros((0,2),dtype=np.uint32)
        self.positions = np.zeros((0,7),dtype=np.float32)

    @classmethod
    def from_file(cls, path="labels.h5"):
        """
        Reads from hdf5 file

        # Attributes
        path(str):
        """
        file = h5.File(path,"r")
        label = cls()
        label.positions = file["labels"][:]
        label.events = file["events"][:]
        label.status = file["status"][:]
        file.close()
        return label

    def save(self,path="labels.h5"):
        """
        Saves label to hdf5

        # Attributes
        path(str):
        """
        file = h5.File(path,"w")
        file["events"] = self.events
        file["labels"] = self.positions
        file["status"] = self.status
        file.close()