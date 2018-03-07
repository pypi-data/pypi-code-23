import os
import boto3
import pandas as pd
import numpy as np
import pickle as pkl
import logging
import json
import glob

from nilearn import image as nimage
from nilearn import plotting as nilplot
import nibabel as nib

class DataSet:
    def __init__(self, D, name="default"):
        self.D = D
        self.n, self.d = self.D.shape
        self.name = name

    def getResource(self, index):
        return self.D.iloc[index, :]

    def saveMetaData(self, filepath):
        metadata = dict(d=self.d, n=self.n, name=self.name)
        string = json.dumps(metadata, indent=2)
        with open(filepath, 'w') as f:
            f.write(string)
        return string

    def getMatrix(self):
        return self.D.as_matrix()

class BIDSParser:

    def __init__(self, base_path):
        dataset_name = os.path.basename(os.path.normpath(base_path))
        dataset = {}
        subjects = [os.path.basename(x) for x in glob.glob(base_path + "/*")]
        if "chanlocs.csv" in subjects:
            subjects.remove("chanlocs.csv")
        if "metadata.json" in subjects:
            subjects.remove("metadata.json")
        print(base_path)
        print(subjects)
        for s in subjects:
            dataset.update({s:{}})
        for s in subjects:
            modalities = [os.path.basename(x) for x in glob.glob(os.path.join(base_path, s) + "/*")]
            print(modalities)
            for m in modalities:
                dataset[s].update({m:{}})
                files = [os.path.basename(x) for x in glob.glob(os.path.join(base_path, s, m) + "/*")]
                print(files)
                for f in files:
                    t = "".join(f.split("_")[1:]).split(".")[0]
                    dataset[s][m].update({t:f})
        self.dataset = dataset
        self.base_path = base_path
        print(self.dataset)

    def getModalityFrame(self, modality, extension):
        files = []
        subjects = []
        tasks = []
        for s in self.dataset.keys():
            for t in self.dataset[s][modality].keys():
                f = self.dataset[s][modality][t]
                if f.endswith(extension):
                    files.append(os.path.join(self.base_path, s, modality, f))
                    subjects.append(s)
                    tasks.append(t)
        d = {
            "resource_path": files,
            "subjects": subjects,
            "tasks": tasks        
        }
        return pd.DataFrame(d)

class fMRIDataSet:

    def __init__(self, dataframe_descriptor, name="fmri"):
        self.D = dataframe_descriptor
        self.D.index = self.D["subjects"] + "-" + self.D["tasks"]
        self.D.index.name = "index"
        self.name = name
        self.n = self.D.shape[0]

    def getResource(self, index):
        resource = self.D.ix[index]
        return resource

    def getMatrix(self, index):
        resource_path = self.D.ix[index][0]
        return nib.load(resource_path).get_data()

class EEGDataSet:

    def __init__(self, dataframe_descriptor, name="fmri"):
        self.D = dataframe_descriptor
        self.D.index = self.D["subjects"].astype(str) + "-" + self.D["tasks"].astype(str)
        self.D.index.name = "index"
        self.name = name
        self.n = self.D.shape[0]

    def getResource(self, index):
        resource = self.D.ix[index]
        return resource

    def getMatrix(self, index):
        resource_path = self.D.ix[index][0]
        with open(resource_path, "rb") as f:
            return pkl.load(f).T

    def getResourceDS(self, index):
        resource = self.getResource(index)
        matrix = self.getMatrix(index)
        D = pd.DataFrame(matrix.T)
        name = "%s/%s"%(resource[1], resource[2])
        DS = DataSet(D, name)
        return DS

class GraphDataSet:

    def __init__(self, dataframe_descriptor, name="fmri"):
        self.D = dataframe_descriptor
        self.D.index = self.D["subjects"].astype(str) + "-" + self.D["tasks"].astype(str)
        self.D.index.name = "index"
        self.name = name
        self.n = self.D.shape[0]

    def getResource(self, index):
        resource = self.D.ix[index]
        return resource

    def getMatrix(self, index):
        resource_path = self.D.ix[index][0]
        try:
            return nx.read_graphml(files)
        except:
            return nx.read_gpickle(files)


class DiskDataSet:
    """A dataset living locally on the hard disk.

    A disk data set is defined by a `.csv` file where entries of the `resource_path` column 
    are paths to local `.pkl` files, and all other columns describe variables of the data point 
    linked to by the `resource_path` variable. 

    Parameters
    ----------
    df_path : str
	Path to the .csv file describing the DiskDataSet.

    Attributes
    ----------
    D : pandas DataFrame
        A DataFrame object describing the dataset.
    N : int
        The number of observations in the dataset.
    name : string
        A descriptive name for the dataset.

    """

    def __init__(self, df_path, index_column = None):
        self.D = pd.read_csv(df_path)
        if index_column is not None:
            self.D.index = self.D[index_column]
            self.D.index.name = index_column
        self.n = self.D.shape[0]
        self.name = df_path.split("/")[-1].split(".")[0].split("_")[0]

    def getResource(self, index):
        """Get a specific data point from the data set.

        Parameters
        ----------
        index : int
            The index of the data point in `D`.

        Returns
        -------
        :obj:`ndarray`
            A ndarray of the data point.

        """
        resource_path = self.D["resource_path"].ix[index]
        dim_column = self.D["dim_column"].ix[index]
        with open(resource_path, "rb") as f:
            if dim_column:
                return pkl.load(f).T
            return pkl.load(f)

    def getResourceDS(self, index):
        D = pd.DataFrame(self.getResource(index).T)
        name = self.name + " " + \
               str(index) + " "
        DS = DataSet(D, name)
        return DS

class CloudDataSet:
    """A dataset living in the cloud in S3.

    A cloud data set lives in S3 with a connection defined by a `.csv` file which
    contains the parameters for a user's bucket.


    Parameters
    ----------
    df_path : str
	Path to the .csv file describing the CloudDataSet.

    Attributes
    ----------
    D : pandas DataFrame
        A DataFrame object describing the dataset.
    N : int
        The number of observations in the dataset.
    name : string
        A descriptive name for the dataset.

    """

    def __init__(self, df_path):
        credential_info = open(df_path, 'r').readlines()
        self.client = boto3.client(
            's3',
            aws_access_key_id=credential_info[1][:-1],
            aws_secret_access_key=credential_info[2],
        )
        self.bucket_name = credential_info[0][:-1]
        self.objects = self.client.list_objects(self.bucket_name)['Contents']

    def getResource(self, index):
        """Get a specific data point from the data set.

        Parameters
        ----------
        index : int
            The index of the data point in `D`.

        Returns
        -------
        :obj:`ndarray`
            A ndarray of the data point.

        """
        self.client.download_file(self.bucket_name, index)

    def getResourceDS(self, index):
        D = pd.DataFrame(self.getResource(index).T)
        name = self.name + " " + \
               str(index) + " "
        DS = DataSet(D, name)
        return DS

def convertDtype(l):
    try:
        return np.array(l, dtype="float")
    except:
        pass
    l = np.array(l, dtype=str)
    l[l == 'nan'] = 'NA'
    return l

class CSVDataSet(DataSet):
    """ A dataset living locally in a .csv file

    """
    def __init__(self, csv_path, index_column = None,  NA_val = ".", name = "mydataset"):
        self.name = name
        
        # Load the data set
        D = pd.read_csv(csv_path, dtype="unicode")
        self.n, self.d = D.shape
        print("Dataset of size", self.n, "samples", self.d, "dimensions", "Loaded")

        # Convert to numeric all numeric rows
        D = D.replace(NA_val, "nan")
        print("Replacing all", NA_val, "with nan")
        d = []
        for c in D.columns:
            d.append(convertDtype(list(D[c])))
            print("Converting", c, end="\r\r") 
        newcolumns = D.columns
        newindex = D.index
        D = list(d)
        D = pd.DataFrame(dict(zip(newcolumns, D)), index = newindex)


        # Set the index column as specified
        if index_column is not None:
            print("Setting index column as", index_column)
            D.index = D[index_column]
            print("Deleting", index_column, "from dataset")
            del D[index_column]

        self.D = D

        # Remove all columns which have all null values
        keep = []
        allnull = self.D.isnull().all(axis=0)
        for c in self.D.columns[allnull]:
            print("Removing column", c, "because it has all null values")
        keep = self.D.columns[~allnull]
        self.D = self.D[keep]

        # Remove all rows which have all null values
        allnull = self.D.isnull().all(axis=1)
        for r in self.D.index[allnull]:
            print("Removing row", r, "because it has all null values")
        keep = self.D.index[~allnull]
        self.D = self.D.loc[keep]
        n, d = self.D.shape
        print("Dataset of size", n, "samples", d, "dimensions", "Resulting")
        self.N = self.D.shape[0]

    def imputeColumns(self, numeric):
        keep = []
        keep = (self.D.dtypes == "float64").as_matrix()
        for c in self.D.columns[~keep]:
            print("Removing column", c, "because it is not numeric")
        self.D = self.D[self.D.columns[keep]]
        cmean = self.D.mean(axis=0)
        values = dict(list(zip(self.D.columns, cmean.as_matrix())))
        #self.D.fillna(value=values, inplace=True)
        d = self.D.as_matrix()
        for i, c in enumerate(self.D.columns):
            print("Imputing column", c, "with value", values[c])
            d[:, i][np.isnan(d[:, i])] = values[c]
        D = pd.DataFrame(d)
        D.index = self.D.index
        D.index.names = self.D.index.names
        D.columns = self.D.columns
        D.columns.names = self.D.columns.names
        self.D = D
        allzero = np.all(self.D.as_matrix() == 0, axis=0)
        for c in self.D.columns[allzero]:
            print("Removing column", c, "because it has all zero values")
        keep = self.D.columns[~allzero]
        allsame = np.std(self.D.as_matrix(), axis=0) == 0
        for c in self.D.columns[allsame]:
            print("Removing column", c, "because it has all zero standard deviation (all values same)")
        keep = self.D.columns[~allsame]
        self.D = self.D[keep]
        n, d = self.D.shape
        print("Dataset of size", n, "samples", d, "dimensions", "Resulting")
        print("Dataset has", self.D.isnull().sum().sum(), "nans")
        print("Dataset has", np.sum(np.isinf(self.D.as_matrix())), "infs")

    def getResource(self, index):
        """Get a specific data point from the data set.

        Parameters
        ----------
        index : int or string
            The index of the data point in `D`, either positional or a string.

        Returns
        -------
        :obj:`ndarray`
            A ndarray of the data point.

        """
        if type(index) is int:
            return self.D.iloc[index].as_matrix()
        else:
            return self.D.loc[index].as_matrix()

    def getColumn(self, index):
        """Get a column of the dataframe.
 
        Parameters
        ----------
        index : int or string
            The index of the column in `D`, either positional or a string.

        Returns
        -------
        :obj:`ndarray`
            The values in the column.
        """
        if type(index) is int:
            return self.D.iloc[:, index].as_matrix()
        else:
            return self.D[index].as_matrix()

    def getColumnValues(self, index):
        """Get the unique values of a column.

        Parameters
        ----------
        index : int or string
            The index of the column in `D`, either positional or a string.

        Returns
        -------
        :obj:`ndarray`
            A ndarray of the unique values.

        """
        column = self.getColumn(index)
        if column.dtype == "float64":
            column = column[~np.isnan(column)]
        else:
            column = column[np.array([x != "NA" for x in column])]
        return np.unique(column)


    def getColumnDistribution(self, index):
        """Get the distribution of values in a column.

        Parameters
        ----------
        index : int or string
            The index of the column in `D`, either positional or a string.

        Returns
        -------
        :obj:`ndarray`, :obj:`ndarray`
            An array x of the unique labels, and an array y of the count of that label

        """
        x = self.getColumnValues(index)
        column = self.getColumn(index)
        y = [np.sum(column == v) for v in x]
        return x, y

    def getColumnNADist(self, index):
        column = self.getColumn(index)
        if column.dtype == "float64":
            na = np.sum([np.isnan(x) for x in column])
            not_na = len(column) - na
            return na, not_na
        else:
            na = np.sum([x == "NA" for x in column])
            not_na = len(column) - na
            return na, not_na
        return na, not_na

    def getColumnDescription(self, index, sep = "\n"):
        """Get a description of the column.

        """
        desc = []
        if type(index) is int:
            index = self.D.columns.values[index]
        for i, name in enumerate(self.D.columns.names):
            desc.append(name + ": " + index[i])
        return sep.join(desc)

    def getLevelValues(self, index):
        return np.unique(self.D.columns.get_level_values(index))


class DistanceMatrix:
    """A distance matrix computed from a DataSet object.

    Parameters
    ----------
    dataset : :obj:`DiskDataSet`
        A dataset on which to compute the distance matrix
    metric : function
        A distance used to compute the distance matrix.

    Attributes
    ----------
    dataset : :obj:`DiskDataSet`
        A dataset on which to compute the distance matrix
    metric : function
        A distance used to compute the distance matrix.
    N : int
        Number of data points in the dataset.
    matrix : :obj:`ndarray`
        The distance matrix.

    """

    def __init__(self, dataset, metric):
        self.DS = dataset
        self.name = self.DS.name
        self.labels = self.DS.D.index.values
        self.label_name = self.DS.D.index.name
        self.metric = metric
        self.metric_name = metric.__name__
        self.n = self.DS.n
        parameterization = self.metric.parameterize(self.DS)
        self.D = np.zeros([self.n, self.n])
        for i in range(self.n):
            I = parameterization[i]
            for j in range(i + 1):
                J = parameterization[j]
                self.D[i, j] = self.metric.compare(I, J)
                self.D[j, i] = self.D[i, j]
        self.D = pd.DataFrame(self.D)
        self.D.index = self.DS.D.index
        self.D.index.name = self.DS.D.index.name

    def getMatrix(self):
        """Get the distance matrix.

        Returns
        -------
        :obj:`ndarray`
            The distance matrix.

        """
        return self.D

class InterpointMatrix:

    def __init__(self, dataset, metric):
        self.DS = dataset
        self.name = self.DS.name
        self.metric = metric
        self.metric_name = metric.__name__
        self.d = self.DS.d
        self.D = np.zeros([self.d, self.d])
        for i in range(self.d):
            I = self.dataset.D.iloc[:, i]
            for j in range(i + 1):
                J = self.DS.D.iloc[:, j]
                self.D[i, j] = self.metric.compare(I, J)
                self.D[j, i] = self.D[i, j]
        self.D = pd.DataFrame(self.D)
        self.D.index = self.DS.D.columns
        self.D.index.name = self.DS.D.index.name

    def getMatrix(self):
        """Get the distance matrix.

        Returns
        -------
        :obj:`ndarray`
            The distance matrix.

        """
        return self.D
