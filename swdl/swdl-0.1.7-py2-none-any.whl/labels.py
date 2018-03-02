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

    def set_position(self, timestamp, target_position, actual_position):
        """
        Adds a position to the given timestamp

        # Arguments:
        timestamp (int): video time in ms
        target_position (array): x, y and z where the camera should look at
        actual_position (array): x, y and z where the camera actually looking at
        """
        row = int(timestamp/100)
        if self.positions.shape[0] < row + 1:
            self.positions.resize((row+1,7), refcheck=False)
            a = actual_position
            t = target_position
            item = [timestamp,t[0],t[1],t[2],a[0],a[1],a[2]]
            self.positions[row] = item
