import requests
import base64
import json
import numpy as np
import os
import pandas as pd


def create_instance_from_grid(baseurl,instance_name,grid_name,scoring_criteria,username,b64password
                              ,angel_type,Pivots,Probability,AcceptedError,
                              PivotSampleSize,CacheSize,IndexCount,MaximumBytesPerObject,
                              IndexSampleSize,Storage,Parallelism,columns_str):
    """
    Create angel from grid results table using cloud/filterThresholdResults?instanceName=X&version=Y API resource.
    """
    query_URL = baseurl + '/filterThresholdResults?instanceName='+grid_name+'&version=V1'

    # Query response 
    resp_query = requests.get(query_URL, auth=(username, b64password))   

    # Getting grid results table, decoding column headers from base32
    decoded_results={}
    rows = []
    for experiment in json.loads(resp_query.content.decode())['elements']:
        for item in experiment.items():
            key , value = item
            key_list = [key, key + '=',key + '===', key + '====', key + '======']
            decoded = False
            while not decoded:
                for key_ in key_list:
                    try:
                        decoded_results[base64.b32decode(key_).decode()] = value
                        decoded = True
                        break
                    except:
                        pass
        rows.append(list(decoded_results.values()))
    
    if type(scoring_criteria) == str:
        grid_table = pd.DataFrame(rows,columns = list(decoded_results.keys())).sort_values(scoring_criteria,ascending=False)
    elif type(scoring_criteria) == list:
        grid_table = pd.DataFrame(rows,columns = list(decoded_results.keys())).sort_values(scoring_criteria,ascending=[False] * len(scoring_criteria))
    else:
        raise TypeError("scoring_citeria can only be a string or a list.")
    
    # Best configuration based on scoring criteria
    angel_to_create = grid_table.iloc[0]
    
    if angel_type.lower() == 'leliel':
        Bins = angel_to_create['BINS']
        K = angel_to_create['K']
        TopColumns = angel_to_create['TOP_COLUMNS']
        Length = angel_to_create['LENGTH']
        EnergyWeight = angel_to_create['ENERGY_WEIGHT']
        Threshold = angel_to_create['threshold']
        ClassificationK = angel_to_create['CLASSIFICATION_K']
        DenseMode = angel_to_create['DENSE_MODE']
        fixedK = '_@_@_FIXED_K=false' if ClassificationK == '-1' else '_@_@_FIXED_K=true'
        
        params_str = columns_str + '_@_@_K=' + K + '_@_@_PIVOTS=' + Pivots + '_@_@_PROBABILITY=' + \
                    Probability + '_@_@_ACCEPTED_ERROR=' + AcceptedError + '_@_@_TOP_COLUMNS=' +  \
                    TopColumns + '_@_@_DENSE_MODE=' + DenseMode + '_@_@_ENERGY_WEIGHT=' + \
                    EnergyWeight + '_@_@_THRESHOLD=' + Threshold + '_@_@_BINS=' + \
                    Bins + '_@_@_LENGTH=' + Length + fixedK +'_@_@_CLASSIFICATION_K=' + ClassificationK + \
                    '_@_@_EXECUTE_GRID=false' + '_@_@_PIVOT_SAMPLE_SIZE=' + \
                    PivotSampleSize + '_@_@_CACHE_SIZE=' + CacheSize + '_@_@_INDEX_COUNT=' + \
                    IndexCount + '_@_@_MAXIMUM_BYTES_PER_OBJECT=' + \
                    MaximumBytesPerObject + '_@_@_INDEX_SAMPLE_SIZE=' + IndexSampleSize
    else:
        Iterations = angel_to_create['ITERATIONS']
        FeatureFocus = angel_to_create['FEATURE_FOCUS']
        FeatureSubsampling = angel_to_create['FEATURE_SUBSAMPLING']
        LearningRate = angel_to_create['LEARNING_RATE']
        ClassWeighting = angel_to_create['CLASS_WEIGHTING']
        Seed = angel_to_create['SEED']
        EnergyWeight = angel_to_create['ENERGY_WEIGHT']
        Bins = angel_to_create['BINS']
        K = angel_to_create['K']
        TopColumns = angel_to_create['TOP_COLUMNS']
        Threshold = angel_to_create['threshold']
        ClassificationK = angel_to_create['CLASSIFICATION_K']
        fixedK = '_@_@_FIXED_K=false' if ClassificationK == '-1' else '_@_@_FIXED_K=true'
        DenseMode = angel_to_create['DENSE_MODE']
        
        params_str = columns_str + '_@_@_K=' + K + '_@_@_PIVOTS=' + Pivots + '_@_@_PROBABILITY=' + \
                    Probability + '_@_@_ACCEPTED_ERROR=' + AcceptedError + '_@_@_TOP_COLUMNS=' + \
                    TopColumns + '_@_@_DENSE_MODE=' + DenseMode + '_@_@_ENERGY_WEIGHT=' + EnergyWeight + \
                    '_@_@_THRESHOLD=' + Threshold + '_@_@_BINS=' + Bins + fixedK +'_@_@_CLASSIFICATION_K='  + \
                    ClassificationK + '_@_@_EXECUTE_GRID=false' +  '_@_@_ITERATIONS=' + \
                    Iterations + '_@_@_LEARNING_RATE=' + LearningRate + '_@_@_FEATURE_FOCUS=' + \
                    FeatureFocus + '_@_@_CLASS_WEIGHTING=' + ClassWeighting + '_@_@_FEATURE_SUBSAMPLING=' + \
                    FeatureSubsampling + '_@_@_PIVOT_SAMPLE_SIZE=' + \
                    PivotSampleSize + '_@_@_CACHE_SIZE=' + CacheSize + '_@_@_INDEX_COUNT=' + \
                    IndexCount + '_@_@_MAXIMUM_BYTES_PER_OBJECT=' + MaximumBytesPerObject + \
                    '_@_@_INDEX_SAMPLE_SIZE=' + IndexSampleSize + '_@_@_SEED=' + Seed    
                      
    return angel_to_create , params_str


class GridSearchCV():
    """
    Executes a grid and selects best model hyper-parameters based on scoring criteria chosen by user. 
    
    Parameters
    ----------
    authenticate_creds: dictionary. simMachines.Authenticate.credentials should be passed here.\n
    DataUploaded: boolean (default = True). If training data already uploaded to simMachines's software, set to True. If not, set to False and angels can be trained on new data not yet uploaded to the software by passing variables X and y to the classifier.\n
    FileName: string (default = ''). Name of the data file if new data is being used to train classifier. Optional, not needed if DataUploaded = True. \n
    specs: dictionary (default = {}). Data specification types for training data. Dictionary keys represent the header names, and the values represent the data types. Optional, highly recommended if DataUploaded = False.\n
    folderName: string (default = ''), Name of folder containing training data.\n
    specFileName: string (default = ''), Name of spec file to use for training. If empty, the most recent compatible file will be chosen.\n
    verbose: bool (default = True). Enable verbose output\n
    angel: string (default = ''). Type of angel to execute grid experiment and select model (Acceptable: 'LELIEL' or 'LELIEL_ALJUNIED').\n
    param_grid: dictionary. Dictionary with parameters names (string) as keys and list of parameters settings to try as values. This enables searching over any sequence of parameter settings.\n
    scoring: string or list/tuple (default = ''). Scoring metric to evaluate goodness of model. Can be any, or any combination, of the following:\n 
    \taccuracy, log_loss, auc_score, mcc, count_CLASS_NAME, recall_CLASS_NAME, precision_CLASS_NAME, f1-score_CLASS_NAME\n
    cv: string (default: 'NFold'). Type of cross-validation experiment to run ('NFold' or 'DateSplit')
    """
    def __init__(self, authenticate_creds, *, DataUploaded = True, FileName = ''
                   , folderName = '', specFileName = '',verbose=True
                   , angel='', param_grid={}, scoring = ''
                   , cv = 'NFold', specs = {}):
        self.filepassword = authenticate_creds['filepassword']
        self.username = authenticate_creds['username']
        self.b64password = authenticate_creds['b64password']
        self.https = authenticate_creds['https']
        self.path = authenticate_creds['path']
        self.port = authenticate_creds['port']

        
        ## Second verification of username and password
        verify_URL = 'https' + '://' + self.path + ':' + self.port + '/cloud/verifyUser' if self.https else 'http' + '://' + self.path + ':' + self.port + '/cloud/verifyUser'
        resp_verify = requests.get(verify_URL,auth=(self.username, self.b64password))
        if resp_verify.status_code != 200:
            raise AttributeError("Username-Password combination not recognized. Please try again.")
            
        self.FileName = FileName
        self.DataUploaded = DataUploaded
        self.folderName = folderName
        self.specFileName = specFileName
        self.verbose = verbose
        self.param_grid = param_grid
        self.scoring = scoring
        self.cv = cv
        self.specs = specs
        self.angel = angel

        
        # Building base URL's
        base_cloud_url = 'https' + '://' + self.path + ':' + self.port + '/cloud' if self.https else 'http' + '://' + self.path + ':' + self.port + '/cloud'
        self.base_cloud_url = base_cloud_url
        base_v2_url = 'https' + '://' + self.path + ':' + self.port + '/V2.0' if self.https else 'http' + '://' + self.path + ':' + self.port + '/V2.0'
        self.base_v2_url = base_v2_url

        # Checking if folderName exists
        if not self.DataUploaded:
            listFolders_URL = self.base_cloud_url +'/listFolders'
            resp_folders = requests.get(listFolders_URL,auth=(self.username, self.b64password))
            if resp_folders.status_code == 200:
                resp_folders_json = json.loads(resp_folders.content.decode())
                folder_exists = 0
                for item in resp_folders_json['list']:
                    if item['name'] == self.folderName:
                        folder_exists = 1
            else:
                raise AttributeError(resp_folders.content.decode())
                
            self._folder_exists = folder_exists
            if self._folder_exists:
                raise AttributeError("Folder name '" + self.folderName + "' already exists. Must choose a unique folder name if 'DataUploaded' is set to False")                
            
        # Warnings
        if self.FileName and self.DataUploaded:
            raise Warning("Since 'DataUploaded' = True, 'FileName' will be ignored.")
        if not self.DataUploaded and not self.specs:
            raise Warning("Data type specifications ('specs') not provided. Automated specification types will be used in model creation. However, it is recommended that spec files are created by the user to improve model performence.")
        if not self.DataUploaded and self.specFileName:
            raise Warning("A spec file name was provided for data not yet uploaded to simMachines's software. 'specFileName' will be ignored.")

        # Exceptions
        if not self.FileName and not self.DataUploaded:
            raise AttributeError('Missing file name (FileName) for data to be uploaded.')
        if not self.folderName:
            raise AttributeError("Must specify name of folder to train Leliel with ('folderName' variable).")
        if not self.angel:
            raise AttributeError("Angel type not specified.")
        if not self.scoring:
            raise AttributeError("Scoring criteria must be specified.")
        
    def fit(self, * ,X='', y='', instanceName = '', gridName = ''):
        """
        Execute grid and select best model based on scoring criteria.
        
        Parameters
        ----------
        X: array or pandas DataFrame, optional (default = ''), shape = (n_samples, n_features). Training data. If X is an array, the first row must be the headers. If X is a pandas DataFrame, the column names will be used as the headers. Optional, only needed if 'DataUploaded' is set to False.\n 
        y: array or pandas Series, optional (default =''), shape = (n_samples,). Target values. If y is an array, the first value must be the header. If y is a pandas Series, the name of the Series will be used as the header. Optional, only needed if 'DataUploaded' is set to False.\n
        instanceName: string (default = ''). Name of instance to be trained.\n
        gridName: string (default = ''). Name of grid to be executed.\n
        
        Returns
        ---------
        self: object. Returns self.
        
        """
        if gridName and instanceName:
            self.gridName = gridName
            self.instanceName = instanceName
            if self.DataUploaded:
                ## Warnings
                if isinstance(X,pd.DataFrame):
                    print("Warning: Since 'DataUploaded' = True, 'X' will be ignored.")
                elif isinstance(X,pd.Series):
                    print("Warning: Since 'DataUploaded' = True, 'X' will be ignored.")
                else: 
                    if type(X) == str and X:
                       print("Warning: Since 'DataUploaded' = True, 'X' will be ignored.")
                    else:
                        if len(X) > 0:
                            print("Warning: Since 'DataUploaded' = True, 'X' will be ignored.")           
                
                if isinstance(y,pd.DataFrame):
                    print("Warning: Since 'DataUploaded' = True, 'X' will be ignored.")
                elif isinstance(y,pd.Series):
                    print("Warning: Since 'DataUploaded' = True, 'X' will be ignored.")
                else: 
                    if type(y) == str and y:
                       print("Warning: Since 'DataUploaded' = True, 'X' will be ignored.")
                    else:
                        if len(y) > 0:
                            print("Warning: Since 'DataUploaded' = True, 'X' will be ignored.")        
                    
                ## getting Specs from folder
                specs_URL = self.base_cloud_url +'/listSpecByFolder?folderName=' + self.folderName
                resp_specs = requests.get(specs_URL,auth=(self.username, self.b64password))
                if resp_specs.status_code == 200:
                    specs_json = json.loads(resp_specs.content.decode())
                    columns_str = 'COLUMNS='
                    valid_specFileName = 0
                    createdDate = 0
                    for spec_file in specs_json['list']:
                        if self.angel in spec_file['angelName']:
                            if self.specFileName:
                                if self.specFileName == spec_file['fileName']:
                                    valid_specFileName = 1
                                    for col in spec_file['specsMap'].keys():
                                        columnName = col
                                        specType = spec_file['specsMap'][col]
                                        columns_str += columnName + ':' + specType + ','
                            else:
                                ## If specFileName not given by user, choose most 
                                ## recent compatible file present 
                                createdDate_curr = spec_file['createdDate']
                                if createdDate_curr > createdDate:
                                    createdDate = createdDate_curr
                                    for col in spec_file['specsMap'].keys():
                                        columnName = col
                                        specType = spec_file['specsMap'][col]
                                        columns_str += columnName + ':' + specType + ','
                else:
                    raise AttributeError(resp_specs.content.decode())
                
                ## Error message if specFileName not recognized
                if not valid_specFileName and self.specFileName:
                    raise AttributeError("Spec file name not recognized. Make sure to include file extension (.json, .tsv, etc.) in specFileName variable")                

            ## New data not uploaded yet is being used to train angel
            else:                    
                if isinstance(X,pd.DataFrame):
                    HeadersX = list(X.columns)
                    X = np.asarray(X)
                elif isinstance(X,pd.Series):
                    HeadersX = [X.name]
                    X = np.asarray(X)
                else: 
                    if type(X) == str:
                        raise TypeError('X cannot be a string. Acceptable types: pandas Dataframe or numpy array.')
                    else:
                        if len(X) > 0:
                            HeadersX = list(X[0])
                            X = np.asarray(X)
                        else:
                            raise AttributeError("X must be provided if 'DataUploaded' is set to False")
                        
                if isinstance(y,pd.DataFrame):
                    HeaderY = list(y.columns)[0]
                    y = np.asarray(y)
                elif isinstance(y,pd.Series):
                    HeaderY = y.name
                    y = np.asarray(y)
                else:
                    if type(y) == str:
                        raise TypeError("y cannot be a string. Acceptable types: pandas Series, DataFrame or numpy array.")
                    else:
                        if len(y) > 0:
                            HeaderY = list(y[0])
                            y = np.asarray(y)
                        else:
                            raise AttributeError("y must be provided if 'DataUploaded' is set to False")   
                    

                ## Create folder if "folderName" is not already created
                listFolders_URL = self.base_cloud_url +'/listFolders'
                resp_folders = requests.get(listFolders_URL,auth=(self.username, self.b64password))
                if resp_folders.status_code == 200:
                    resp_folders_json = json.loads(resp_folders.content.decode())
                    folder_exists = 0
                    for item in resp_folders_json['list']:
                        if item['name'] == self.folderName:
                            folder_exists = 1
                else:
                    raise AttributeError(resp_folders.content.decode())
                        
                if not folder_exists:
                    createFolder_URL = self.base_cloud_url +'/createFolder'
                    folder_data = {"folderName" : self.folderName}
                    resp_CreateFolder = requests.post(createFolder_URL,data = folder_data,auth=(self.username, self.b64password))
                    if resp_CreateFolder.status_code == 200:
                        pass
                    else:
                        raise AttributeError(resp_CreateFolder.content.decode())
                else:
                    raise AttributeError('Folder with name %s already exists.' % self.folderName)
                    
                ## Upload data to "folderName"
                uploadFile_URL = self.base_cloud_url + '/uploadFile'
                # Validating shape of input data
                if X.shape[0] != y.shape[0]:
                    raise ValueError('X and y have incompatible shapes.')
                    
                if X.shape[1] != len(HeadersX):
                    raise ValueError('X.shape[1] must equal the length of HeadersX')

                # Creating new data stream   
                with open(self.FileName,'wb') as r:
                    ## Header
                    header_string = '\t'.join(HeadersX) + '\t' + str(HeaderY) + '\n'
                    r.write(header_string.encode('utf8'))
                    for i,row in enumerate(X):
                        row_str = '\t'.join([str(val) for val in row.tolist()]) + '\t' +str(y[i])
                        if i == (len(X)-1):
                            pass
                        else:
                            row_str += '\n'
                        r.write(row_str.encode('utf8'))
                    r.flush()
                r.close()
                
                filesize = os.path.getsize(self.FileName)
                
                with open(self.FileName,'rb') as f:
                    file_stream = {'fileData' : f}
                    file_data = {'fileName' : self.FileName
                              ,'fileSize' : filesize
                              ,'folderName' : self.folderName
                              ,'authorization' : self.filepassword
                              }
                    resp_file = requests.post(uploadFile_URL
                                         ,files = file_stream
                                              ,data = file_data
                                              ,auth = (self.username, base64.b64decode(self.b64password).decode()))
                f.close()
                os.remove(self.FileName)
                
                ## Raise error if file upload API call not successfull
                if resp_file.status_code == 200:
                    pass
                else:
                    raise AttributeError(resp_file.content.decode())
                
                ## Create spec file
                columns_str = 'COLUMNS='
                if not self.specs:
                    # Use recommended specs from /getSpecsOfFolder
                    getSpecs_URL = self.base_cloud_url + '/getSpecsOfFolder?folderName=' + self.folderName
                    resp_specs = requests.get(getSpecs_URL,auth=(self.username,self.b64password))
                    if resp_specs.status_code == 200:
                        resp_specs_json = json.loads(resp_specs.content.decode())
                        for item in resp_specs_json['columns']:
                            col_name = item['columnName']
                            if col_name == HeaderY:
                                spec_type = 'CLASS'
                            else:
                                spec_type = item['typeOfColumn']
                            columns_str += col_name + ':' + spec_type + ','
                    else:
                        raise AttributeError(resp_specs.content.decode())
                else:
                    for item in self.specs.items():
                        col_name, spec_type = item
                        if col_name == HeaderY:
                            spec_type = 'CLASS'
                        columns_str += col_name + ':' + spec_type + ','
            

            columns_str = columns_str[:-1]
            
            ## Building CURL command from param_grid
            if self.angel.lower() == 'leliel':
                if self.param_grid:
                    params_lower = [key.lower() for key in self.param_grid.keys()]
                    self.Pivots_grid = '256' if 'pivots' not in params_lower else ';'.join([str(item) for item in self.param_grid['Pivots']]) if type(self.param_grid['Pivots']) in [list,tuple] else self.param_grid['Pivots']
                    self.Probability_grid = '0.95' if 'probability' not in params_lower else ';'.join([str(item) for item in self.param_grid['Probability']]) if type(self.param_grid['Probability']) in [list,tuple] else self.param_grid['Probability']
                    self.AcceptedError_grid = '1.2' if 'acceptederror' not in params_lower else ';'.join([str(item) for item in self.param_grid['AcceptedError']]) if type(self.param_grid['AcceptedError']) in [list,tuple] else self.param_grid['AcceptedError']
                    self.Bins_grid = '10;20;30' if 'bins' not in params_lower else ';'.join([str(item) for item in self.param_grid['Bins']]) if type(self.param_grid['Bins']) in [list,tuple] else self.param_grid['Bins']
                    self.K_grid = '10' if 'k' not in params_lower else ';'.join([str(item) for item in self.param_grid['K']]) if type(self.param_grid['K']) in [list,tuple] else self.param_grid['K']
                    self.TopColumns_grid = '5;10;20' if 'topcolumns' not in params_lower else ';'.join([str(item) for item in self.param_grid['TopColumns']]) if type(self.param_grid['TopColumns']) in [list,tuple] else self.param_grid['TopColumns']
                    self.Length_grid ='2' if 'length' not in params_lower else ';'.join([str(item) for item in self.param_grid['Length']]) if type(self.param_grid['Length']) in [list,tuple] else self.param_grid['Length']
                    self.DenseMode_grid = 'SMART;EXCEEDS;DEFAULT' if 'densemode' not in params_lower else ';'.join([str(item) for item in self.param_grid['DenseMode']]) if type(self.param_grid['DenseMode']) in [list,tuple] else self.param_grid['DenseMode']
                    self.EnergyWeight_grid = True if 'energyweight' not in params_lower else ';'.join([str(item) for item in self.param_grid['EnergyWeight']]) if type(self.param_grid['EnergyWeight']) in [list,tuple] else self.param_grid['EnergyWeight']
                    energy_weight_str = 'true' if self.EnergyWeight_grid else 'false'
                    self.Threshold_grid = '0.5' if 'threshold' not in params_lower else ';'.join([str(item) for item in self.param_grid['Threshold']]) if type(self.param_grid['Threshold']) in [list,tuple] else self.param_grid['Threshold']
                    self.NumberOfThresholds_grid = '100' if 'numberofthresholds' not in params_lower else ';'.join([str(item) for item in self.param_grid['NumberOfThresholds']]) if type(self.param_grid['NumberOfThresholds']) in [list,tuple] else self.param_grid['NumberOfThresholds']                    
                    self.ClassificationK_grid = '-1' if 'classificationk' not in params_lower else ';'.join([str(item) for item in self.param_grid['ClassificationK']]) if type(self.param_grid['ClassificationK']) in [list,tuple] else self.param_grid['ClassificationK']                    
                    fixedK = '_@_@_FIXED_K=false' if self.ClassificationK_grid == '-1' else '_@_@_FIXED_K=true'
                    self.PivotSampleSize_grid = '20000' if 'pivotsamplesize' not in params_lower else self.param_grid['PivotSampleSize']                    
                    self.CacheSize_grid = '1000000' if 'cachesize' not in params_lower else  self.param_grid['CacheSize']                    
                    self.IndexCount_grid = '3' if 'indexcount' not in params_lower else self.param_grid['IndexCount']                    
                    self.MaximumBytesPerObject_grid =  '500000' if 'maximumbytesperobject' not in params_lower else self.param_grid['MaximumBytesPerObject']                    
                    self.IndexSampleSize_grid = '100' if 'indexsamplesize' not in params_lower else self.param_grid['IndexSampleSize']                    
                    self.Storage = 1 if 'storage' not in params_lower else self.param_grid['Storage']
                    self.Parallelism = 2 if 'parallelism' not in params_lower else self.param_grid['Parallelism']
                    if self.cv == 'NFold':
                        experiment_str = 'K_FOLD_CROSS_VALIDATION' 
                        self.n_folds_grid = '3' if 'numberoffolds' not in params_lower else self.param_grid['NumberOfFolds']
                        self.fold_seed_grid = '3423645' if 'foldseed' not in params_lower else self.param_grid['FoldSeed']
                    elif self.cv == 'DateSplit':
                        experiment_str = 'TUNING'
                        try:
                            self.first_split_date_grid = self.param_grid['FirstSplitDate']
                        except KeyError:
                            raise AttributeError("'FirstSplitDate' must be provided in param_grid if running DateSplit experiments.")
                        try:
                            self.second_split_date_grid = self.param_grid['SecondSplitDate']
                        except KeyError:
                            raise AttributeError("'SecondSplitDate' must be provided in param_grid if running DateSplit experiments.")
                        try:
                            self.date_format_grid = self.param_grid['DateFormat']
                        except KeyError:
                            raise AttributeError("'DateFormat' must be provided in param_grid if running DateSplit experiments.")
                        try:
                            self.date_column_grid = self.param_grid['DateColumn']
                        except KeyError:
                            raise AttributeError("'DateColumn' must be provided in param_grid if running DateSplit experiments.")
                    else:
                        raise AttributeError("Incorrect experiment mode ('cv'). Only 'NFold' and 'DateSplit' are acceptable.")
                        
                else:
                    self.Pivots_grid = '256'
                    self.Probability_grid = '0.95'
                    self.AcceptedError_grid = '1.2'
                    self.Bins_grid = '10;20;30'
                    self.K_grid = '10'
                    self.TopColumns_grid = '5;10;20'
                    self.Length_grid = '2'
                    self.DenseMode_grid = 'SMART;EXCEEDS;DEFAULT'
                    self.EnergyWeight_grid = True
                    energy_weight_str = 'true' if self.EnergyWeight_grid else 'false'
                    self.Threshold_grid = '0.5'
                    self.NumberOfThresholds_grid = '100'
                    self.ClassificationK_grid = '-1'
                    fixedK = '_@_@_FIXED_K=false' if self.ClassificationK_grid == '-1' else '_@_@_FIXED_K=true'
                    self.PivotSampleSize_grid = '20000'
                    self.CacheSize_grid = '1000000'
                    self.IndexCount_grid = '3'
                    self.MaximumBytesPerObject_grid =  '500000'
                    self.IndexSampleSize_grid = '100'
                    self.cv = 'NFold'
                    experiment_str = 'K_FOLD_CROSS_VALIDATION' 
                    self.n_folds_grid = '3'
                    self.fold_seed_grid = '3423645'
                    self.Storage = 1
                    self.Parallelism = 2
                params_str = columns_str + '_@_@_K=' + str(self.K_grid) + '_@_@_PIVOTS=' + str(self.Pivots_grid) + '_@_@_PROBABILITY=' + \
                            str(self.Probability_grid) + '_@_@_ACCEPTED_ERROR=' + str(self.AcceptedError_grid) + '_@_@_TOP_COLUMNS=' +  \
                            str(self.TopColumns_grid) + '_@_@_DENSE_MODE=' + str(self.DenseMode_grid) + '_@_@_ENERGY_WEIGHT=' + \
                            energy_weight_str + '_@_@_THRESHOLD=' + str(self.Threshold_grid) + '_@_@_BINS=' + \
                            str(self.Bins_grid) + '_@_@_LENGTH=' + str(self.Length_grid) + fixedK +'_@_@_CLASSIFICATION_K=' + str(self.ClassificationK_grid) + \
                            '_@_@_EXECUTE_GRID=true' + '_@_@_PIVOT_SAMPLE_SIZE=' + \
                            str(self.PivotSampleSize_grid) + '_@_@_CACHE_SIZE=' + str(self.CacheSize_grid) + '_@_@_INDEX_COUNT=' + \
                            str(self.IndexCount_grid) + '_@_@_MAXIMUM_BYTES_PER_OBJECT=' + \
                            str(self.MaximumBytesPerObject_grid) + '_@_@_INDEX_SAMPLE_SIZE=' + str(self.IndexSampleSize_grid)
                if self.cv == 'NFold':
                    params_str +=  '_@_@_EXPERIMENT_MODE=' + experiment_str + '_@_@_NFOLDS=' + str(self.n_folds_grid) + \
                                    '_@_@_FOLD_SEED=' + str(self.fold_seed_grid)
                elif self.cv == 'DateSplit':
                    params_str += '_@_@_EXPERIMENT_MODE=' + experiment_str + '_@_@_FIRST_SPLIT_DATE=' + str(self.first_split_date_grid) + \
                                    '_@_@_SECOND_SPLIT_DATE=' + str(self.second_split_date_grid) + '_@_@_DATE_FORMAT=' + str(self.date_format_grid) + \
                                    '_@_@_DATE_COLUMN=' + str(self.date_column_grid)
                                
                            
            elif self.angel.lower() == 'leliel_aljunied':
                if self.param_grid:
                    params_lower = [key.lower() for key in self.param_grid.keys()]
                    self.Pivots_grid = '256' if 'pivots' not in params_lower else ';'.join([str(item) for item in self.param_grid['Pivots']]) if type(self.param_grid['Pivots']) in [list,tuple] else self.param_grid['Pivots']
                    self.Probability_grid = '0.95' if 'probability' not in params_lower else ';'.join([str(item) for item in self.param_grid['Probability']]) if type(self.param_grid['Probability']) in [list,tuple] else self.param_grid['Probability']
                    self.AcceptedError_grid = '1.2' if 'acceptederror' not in params_lower else ';'.join([str(item) for item in self.param_grid['AcceptedError']]) if type(self.param_grid['AcceptedError']) in [list,tuple] else self.param_grid['AcceptedError']
                    self.Bins_grid = '10' if 'bins' not in params_lower else ';'.join([str(item) for item in self.param_grid['Bins']]) if type(self.param_grid['Bins']) in [list,tuple] else self.param_grid['Bins']
                    self.K_grid = '10' if 'k' not in params_lower else ';'.join([str(item) for item in self.param_grid['K']]) if type(self.param_grid['K']) in [list,tuple] else self.param_grid['K']
                    self.TopColumns_grid = '20' if 'topcolumns' not in params_lower else ';'.join([str(item) for item in self.param_grid['TopColumns']]) if type(self.param_grid['TopColumns']) in [list,tuple] else self.param_grid['TopColumns']
                    self.DenseMode_grid = 'SMART;EXCEEDS;DEFAULT' if 'densemode' not in params_lower else ';'.join([str(item) for item in self.param_grid['DenseMode']]) if type(self.param_grid['DenseMode']) in [list,tuple] else self.param_grid['DenseMode']
                    self.EnergyWeight_grid = True if 'energyweight' not in params_lower else ';'.join([str(item) for item in self.param_grid['EnergyWeight']]) if type(self.param_grid['EnergyWeight']) in [list,tuple] else self.param_grid['EnergyWeight']
                    energy_weight_str = 'true' if self.EnergyWeight_grid else 'false'
                    self.Threshold_grid = '0.5' if 'threshold' not in params_lower else ';'.join([str(item) for item in self.param_grid['Threshold']]) if type(self.param_grid['Threshold']) in [list,tuple] else self.param_grid['Threshold']
                    self.NumberOfThresholds_grid = '100' if 'numberofthresholds' not in params_lower else ';'.join([str(item) for item in self.param_grid['NumberOfThresholds']]) if type(self.param_grid['NumberOfThresholds']) in [list,tuple] else self.param_grid['NumberOfThresholds']                    
                    self.ClassificationK_grid = '-1' if 'classificationk' not in params_lower else ';'.join([str(item) for item in self.param_grid['ClassificationK']]) if type(self.param_grid['ClassificationK']) in [list,tuple] else self.param_grid['ClassificationK']                    
                    fixedK = '_@_@_FIXED_K=false' if self.ClassificationK_grid == '-1' else '_@_@_FIXED_K=true'
                    self.PivotSampleSize_grid = '20000' if 'pivotsamplesize' not in params_lower else self.param_grid['PivotSampleSize']                    
                    self.CacheSize_grid = '1000000' if 'cachesize' not in params_lower else self.param_grid['CacheSize']                    
                    self.IndexCount_grid = '3' if 'indexcount' not in params_lower else self.param_grid['IndexCount']                    
                    self.MaximumBytesPerObject_grid =  '500000' if 'maximumbytesperobject' not in params_lower else self.param_grid['MaximumBytesPerObject']                    
                    self.IndexSampleSize_grid = '100' if 'indexsamplesize' not in params_lower else self.param_grid['IndexSampleSize']                    
                    self.Seed_grid = '563131' if 'seed' not in params_lower else self.param_grid['Seed']
                    self.Iterations_grid = '2000;1000;300' if 'iterations' not in params_lower else ';'.join([str(item) for item in self.param_grid['Iterations']]) if type(self.param_grid['Iterations']) in [list,tuple] else self.param_grid['Iterations']                    
                    self.LearningRate_grid = '0.05;0.01;0.3' if 'learningrate' not in params_lower else ';'.join([str(item) for item in self.param_grid['LearningRate']]) if type(self.param_grid['LearningRate']) in [list,tuple] else self.param_grid['LearningRate']                    
                    self.FeatureSubsampling_grid = '0.5;1.0' if 'featuresubsampling' not in params_lower else ';'.join([str(item) for item in self.param_grid['FeatureSubsampling']]) if type(self.param_grid['FeatureSubsampling']) in [list,tuple] else self.param_grid['FeatureSubsampling']                    
                    self.FeatureFocus_grid = '5;10;20' if 'featurefocus' not in params_lower else ';'.join([str(item) for item in self.param_grid['FeatureFocus']]) if type(self.param_grid['FeatureFocus']) in [list,tuple] else self.param_grid['FeatureFocus']
                    self.ClassWeighting_grid = 'UNIFORM;NORMALIZED' if 'classweighting' not in params_lower else ';'.join([str(item) for item in self.param_grid['ClassWeighting']]) if type(self.param_grid['ClassWeighting']) in [list,tuple] else self.param_grid['ClassWeighting']
                    self.Storage = 1 if 'storage' not in params_lower else self.param_grid['Storage']
                    self.Parallelism = 2 if 'parallelism' not in params_lower else self.param_grid['Parallelism']
                    if self.cv == 'NFold':
                        experiment_str = 'K_FOLD_CROSS_VALIDATION' 
                        self.n_folds_grid = '3' if 'numberoffolds' not in params_lower else self.param_grid['NumberOfFolds']
                        self.fold_seed_grid = '3423645' if 'foldseed' not in params_lower else self.param_grid['FoldSeed']
                    elif self.cv == 'DateSplit':
                        experiment_str = 'TUNING'
                        try:
                            self.first_split_date_grid = self.param_grid['FirstSplitDate']
                        except KeyError:
                            raise AttributeError("'FirstSplitDate' must be provided in param_grid if running DateSplit experiments.")
                        try:
                            self.second_split_date_grid = self.param_grid['SecondSplitDate']
                        except KeyError:
                            raise AttributeError("'SecondSplitDate' must be provided in param_grid if running DateSplit experiments.")
                        try:
                            self.date_format_grid = self.param_grid['DateFormat']
                        except KeyError:
                            raise AttributeError("'DateFormat' must be provided in param_grid if running DateSplit experiments.")
                        try:
                            self.date_column_grid = self.param_grid['DateColumn']
                        except KeyError:
                            raise AttributeError("'DateColumn' must be provided in param_grid if running DateSplit experiments.")
                    else:
                        raise AttributeError("Incorrect experiment mode ('cv'). Only 'NFold' and 'DateSplit' are acceptable.")
                else:
                    self.Pivots_grid = '256'
                    self.Probability_grid = '0.95'
                    self.AcceptedError_grid = '1.2'
                    self.Bins_grid = '10'
                    self.K_grid = '10'
                    self.TopColumns_grid = '20'
                    self.DenseMode_grid = 'SMART;EXCEEDS;DEFAULT'
                    self.EnergyWeight_grid = True
                    energy_weight_str = 'true' if self.EnergyWeight_grid else 'false'
                    self.Threshold_grid = '0.5'
                    self.NumberOfThresholds_grid = '100'
                    self.ClassificationK_grid = '-1'
                    fixedK = '_@_@_FIXED_K=false' if self.ClassificationK_grid == '-1' else '_@_@_FIXED_K=true'
                    self.PivotSampleSize_grid = '20000'
                    self.CacheSize_grid = '1000000'
                    self.IndexCount_grid = '3'
                    self.MaximumBytesPerObject_grid =  '500000'
                    self.IndexSampleSize_grid = '100'          
                    self.Seed_grid = '563131'
                    self.Iterations_grid = '2000;1000;300'
                    self.LearningRate_grid = '0.05;0.01;0.3'
                    self.FeatureSubsampling_grid = '0.5;1.0'
                    self.FeatureFocus_grid = '5;10;20'
                    self.ClassWeighting_grid = 'UNIFORM;NORMALIZED'
                    self.Storage = 1
                    self.Parallelism = 2
                    experiment_str = 'K_FOLD_CROSS_VALIDATION' 
                    self.n_folds_grid = '3'
                    self.fold_seed_grid = '3423645'
                params_str = columns_str + '_@_@_K=' + str(self.K_grid) + '_@_@_PIVOTS=' + str(self.Pivots_grid) + '_@_@_PROBABILITY=' + \
                            str(self.Probability_grid) + '_@_@_ACCEPTED_ERROR=' + str(self.AcceptedError_grid) + '_@_@_TOP_COLUMNS=' + \
                            str(self.TopColumns_grid) + '_@_@_DENSE_MODE=' + str(self.DenseMode_grid) + '_@_@_ENERGY_WEIGHT=' + energy_weight_str + \
                            '_@_@_THRESHOLD=' + str(self.Threshold_grid) + '_@_@_BINS=' + str(self.Bins_grid) + fixedK +'_@_@_CLASSIFICATION_K=' + \
                            str(self.ClassificationK_grid) + '_@_@_EXECUTE_GRID=true' +  '_@_@_ITERATIONS=' + \
                            str(self.Iterations_grid) + '_@_@_LEARNING_RATE=' + str(self.LearningRate_grid) + '_@_@_FEATURE_FOCUS=' + \
                            str(self.FeatureFocus_grid) + '_@_@_CLASS_WEIGHTING=' + str(self.ClassWeighting_grid) + '_@_@_FEATURE_SUBSAMPLING=' + \
                            str(self.FeatureSubsampling_grid) + '_@_@_PIVOT_SAMPLE_SIZE=' + \
                            str(self.PivotSampleSize_grid) + '_@_@_CACHE_SIZE=' + str(self.CacheSize_grid) + '_@_@_INDEX_COUNT=' + \
                            str(self.IndexCount_grid) + '_@_@_MAXIMUM_BYTES_PER_OBJECT=' + str(self.MaximumBytesPerObject_grid) + \
                            '_@_@_INDEX_SAMPLE_SIZE=' + str(self.IndexSampleSize_grid) + '_@_@_SEED=' + str(self.Seed_grid)
                if self.cv == 'NFold':
                    params_str +=  '_@_@_EXPERIMENT_MODE=' + experiment_str + '_@_@_NFOLDS=' + str(self.n_folds_grid) + \
                                    '_@_@_FOLD_SEED=' + str(self.fold_seed_grid)
                elif self.cv == 'DateSplit':
                    params_str += '_@_@_EXPERIMENT_MODE=' + experiment_str + '_@_@_FIRST_SPLIT_DATE=' + str(self.first_split_date_grid) + \
                                    '_@_@_SECOND_SPLIT_DATE=' + str(self.second_split_date_grid) + '_@_@_DATE_FORMAT=' + str(self.date_format_grid) + \
                                    '_@_@_DATE_COLUMN=' + str(self.date_column_grid)    
                
            ## Building API call
            grid_data = {"instanceName" : self.gridName,
                             "folderName" : self.folderName,
                             "angelName": self.angel,
                             "params": params_str,
                             "storage" : self.Storage,
                             "parallelism" : self.Parallelism,
                             "authorization" : self.filepassword
                    }
            ## POST request to create instance
            createInstance_url = self.base_cloud_url + '/createInstance'
            resp = requests.post(createInstance_url,data = grid_data, auth = (self.username, self.b64password))                
                
            if resp.status_code == 200:
                listInstances_url = self.base_cloud_url + '/listInstances'
                status = 'Unknown'
                while status not in ('COMPLETED', 'BUILD_ERROR'):
                    resp_status = requests.get(listInstances_url, auth=(self.username, self.b64password))
                    if resp_status.status_code == 200:
                        resp_JSON = json.loads(resp_status.content.decode())
                        
                        ## looping through instances
                        for l in resp_JSON['list']:
                            if l['label'] == self.gridName:
                                status_curr = l['status']
                                if status != status_curr:
                                    status = status_curr
                                    if self.verbose:
                                        print('Status: ' + status)
                                    else:
                                        pass
                    else:
                        raise AttributeError(resp_status.content.decode())
                    if status == 'COMPLETED':
                        print("Status: Grid completed, creating angel based on scoring criteria.")
                        break
                    elif status == 'BUILD_ERROR':
                        raise AttributeError("Grid '" + self.gridName + "' returned a status of '" + status + "'.")
                        break
                    elif status == 'CANCELLED':
                        raise AttributeError("Grid '" + self.gridName + " has been cancelled.")
                        break
            else:
                ## If instance not created, set instance name to '' 
                self.gridName = ''
                raise AttributeError(resp.content.decode())
                
            # Getting parameters from best grid config
            angel_to_create, params_best = create_instance_from_grid(self.base_cloud_url,self.instanceName,self.gridName,self.scoring,self.username,self.b64password
                              ,self.angel,self.Pivots_grid,self.Probability_grid,self.AcceptedError_grid,
                              self.PivotSampleSize_grid,self.CacheSize_grid,self.IndexCount_grid,self.MaximumBytesPerObject_grid,
                              self.IndexSampleSize_grid,self.Storage,self.Parallelism,columns_str)

            if self.angel.lower() == 'leliel':
                self.Bins_model = angel_to_create['BINS']
                self.K_model = angel_to_create['K']
                self.TopColumns_model = angel_to_create['TOP_COLUMNS']
                self.Length_model = angel_to_create['LENGTH']
                self.EnergyWeight_model = angel_to_create['ENERGY_WEIGHT']
                self.Threshold_model = angel_to_create['threshold']
                self.ClassificationK_model = angel_to_create['CLASSIFICATION_K']
                self.DenseMode_model = angel_to_create['DENSE_MODE']
                fixedK = '_@_@_FIXED_K=false' if self.ClassificationK_model == '-1' else '_@_@_FIXED_K=true'
            else:
                self.Iterations_model = angel_to_create['ITERATIONS']
                self.FeatureFocus_model = angel_to_create['FEATURE_FOCUS']
                self.FeatureSubsampling_model = angel_to_create['FEATURE_SUBSAMPLING']
                self.LearningRate_model = angel_to_create['LEARNING_RATE']
                self.ClassWeighting_model = angel_to_create['CLASS_WEIGHTING']
                self.Seed_model = angel_to_create['SEED']
                self.EnergyWeight_model = angel_to_create['ENERGY_WEIGHT']
                self.Bins_model = angel_to_create['BINS']
                self.K_model = angel_to_create['K']
                self.TopColumns_model = angel_to_create['TOP_COLUMNS']
                self.Threshold_model = angel_to_create['threshold']
                self.ClassificationK_model = angel_to_create['CLASSIFICATION_K']
                fixedK = '_@_@_FIXED_K=false' if self.ClassificationK_model == '-1' else '_@_@_FIXED_K=true'
                self.DenseMode_model = angel_to_create['DENSE_MODE']

            
            ## Building API call for angel
            instance_data = {"instanceName" : self.instanceName,
                             "folderName" : self.folderName,
                             "angelName": self.angel,
                             "params": params_best,
                             "storage" : self.Storage,
                             "parallelism" : self.Parallelism,
                             "authorization" : self.filepassword
                    }
            ## POST request to create instance
            createInstance_url = self.base_cloud_url + '/createInstance'
            resp = requests.post(createInstance_url,data = instance_data, auth = (self.username, self.b64password))
            
            if resp.status_code == 200:
                listInstances_url = self.base_cloud_url + '/listInstances'
                status = 'Unknown'
                while status not in ('RUNNNING', 'BUILD_ERROR'):
                    resp_status = requests.get(listInstances_url, auth=(self.username, self.b64password))
                    if resp_status.status_code == 200:
                        resp_JSON = json.loads(resp_status.content.decode())
                    
                        ## looping through instances
                        for l in resp_JSON['list']:
                            if l['label'] == self.instanceName:
                                status_curr = l['status']
                                if status != status_curr:
                                    status = status_curr
                                    if self.verbose:
                                        print('Status: ' + status)
                                    else:
                                        pass
                    else:
                        raise AttributeError(resp_status.content.decode())
                        
                    if status == 'RUNNING':
                        print("Instance '" + self.instanceName + "' is ready for querying.")
                        break
                    elif status == 'BUILD_ERROR':
                        print("Instance '" + self.instanceName + "' returned a status of '" + status + "'.")
                        break
                    
            else:
                ## If instance not created, set instance name to '' 
                self.instanceName = ''
                raise AttributeError(resp.content.decode())

        else:
            raise AttributeError("'gridName' and 'instanceName' must be present in fit() call.")
        
        return self

    
    def predict(self, X,*,version = ''):
        """
        Predict using trained angel from grid, returns class.
        
        Parameters
        ----------
        X: {array-like}. Samples to predict. shape = (n_samples, n_features). 
        First line must be headers. 
        
        Returns
        ----------
        y_pred: array, shape = (n_samples,)
        Class labels for samples in X
        """
        
        if self.instanceName:
            if isinstance(X,pd.DataFrame):
                headers = list(X.columns)
                X = np.asarray(X)
            elif isinstance(X,pd.Series):
                headers = [X.name]
                X = np.asarray(X)
            else: 
                if type(X) == str:
                    raise TypeError('X cannot be a string. Acceptable types: pandas Dataframe, Series or numpy array.')
                else:
                    if len(X) > 0:
                        headers = list(X[0])
                        X = np.asarray(X[1:])
                    else:
                        raise AttributeError("X must be provided if 'DataUploaded' is set to False")
            headers_str = '\t'.join(headers)
            samples = X
            y_pred=[]
            if samples.shape[0]> 0:
                failed_queries = 0
                for samp in samples:
                    sample_str = '\t'.join([str(s) for s in samp])
                    queryObject_url = self.base_cloud_url + '/queryObject'
                    if version:
                        query_data = {"instanceName" : self.instanceName,
                                      "version" : version,
                                      "query" : headers_str + '\n' + sample_str,
                                      "authorization" : self.filepassword
                                }
                    else:
                        query_data = {"instanceName" : self.instanceName,
                                      "query" : headers_str + '\n' + sample_str,
                                      "authorization" : self.filepassword
                                }              
                    resp_query = requests.post(queryObject_url,data = query_data, auth = (self.username, self.b64password))
                    if resp_query.status_code == 200:
                        ## Converting response to JSON object
                        resp_query_json = json.loads(resp_query.content.decode())
                        winning_class = resp_query_json['winnerUsingThreshold']['predictedClass']
                        y_pred.append(winning_class)
                    else:
                        failed_queries+=1
                        error_message = resp_query.content.decode()
                        
                if not failed_queries:
                    return np.asarray(y_pred)
                else:
                    raise AttributeError("One or more queries producing errors. API error message: " + error_message + ".")
            else:
                raise AttributeError("Must contain both headers and query objects for prediction.")
                
        else:
            raise AttributeError("Must create instance by using fit() before predicting.")   
            
    
    def predict_confidence(self, X,*,version = ''):
        """
        Predict using a trained instance from a grid, returns confidence score. 
        
        Parameters
        ----------
        X: {array-like}. Samples to predict. shape = (n_samples, n_features). 
        First line must be headers. 
        
        Returns
        ----------
        y_pred: array, shape = (n_samples,)
        Prediction confidences for samples in X
        """
        
        if self.instanceName:
            if isinstance(X,pd.DataFrame):
                headers = list(X.columns)
                X = np.asarray(X)
            elif isinstance(X,pd.Series):
                headers = [X.name]
                X = np.asarray(X)
            else: 
                if type(X) == str:
                    raise TypeError('X cannot be a string. Acceptable types: pandas Dataframe, Series or numpy array.')
                else:
                    if len(X) > 0:
                        headers = list(X[0])
                        X = np.asarray(X[1:])
                    else:
                        raise AttributeError("X must be provided if 'DataUploaded' is set to False")
            headers_str = '\t'.join(headers)
            samples = X
            y_pred=[]
            if samples.shape[0]> 0:
                failed_queries = 0
                for samp in samples:
                    sample_str = '\t'.join([str(s) for s in samp])
                    queryObject_url = self.base_cloud_url + '/queryObject'
                    if version:
                        query_data = {"instanceName" : self.instanceName,
                                      "version" : version,
                                      "query" : headers_str + '\n' + sample_str,
                                      "authorization" : self.filepassword
                                }
                    else:
                        query_data = {"instanceName" : self.instanceName,
                                      "query" : headers_str + '\n' + sample_str,
                                      "authorization" : self.filepassword
                                }              
                    resp_query = requests.post(queryObject_url,data = query_data, auth = (self.username, self.b64password))
                    
                    if resp_query.status_code == 200:
                        ## Converting response to JSON object
                        resp_query_json = json.loads(resp_query.content.decode())
                        winning_score={}
                        for result in resp_query_json['results']:
                            winning_score[result['predictedClass']] = result['score']
                        y_pred.append(winning_score)
                    else:
                        failed_queries += 1
                        error_message = resp_query.content.decode()
                if not failed_queries:
                    return np.asarray(y_pred)
                else:
                    raise AttributeError("One or more queries producing errors. API error message: " + error_message + ".")
            else:
                raise AttributeError("Must contain both headers and query objects for prediction.")
                
        else:
            raise AttributeError("Must create instance by using fit() before predicting.")
            
            
    def get_neighbors(self, X, *,version = ''):
        """
        Retrive nearest neighbors using a trained instance from a grid.
        
        Parameters
        ----------
        X: {array-like}. Samples to retrieve neighbors for. shape = (n_samples, n_features). 
        First line must be headers. 
        
        Returns
        ----------
        neighbors_final: list of dictionaries, shape = (n_samples,(Classification K * Length,2))
        ID, distance pairs of nearest neighbors
        """
        if self.angel.lower() == 'leliel':
            if self.instanceName:
                if isinstance(X,pd.DataFrame):
                    headers = list(X.columns)
                    X = np.asarray(X)
                elif isinstance(X,pd.Series):
                    headers = [X.name]
                    X = np.asarray(X)
                else: 
                    if type(X) == str:
                        raise TypeError('X cannot be a string. Acceptable types: pandas Dataframe, Series or numpy array.')
                    else:
                        if len(X) > 0:
                            headers = list(X[0])
                            X = np.asarray(X[1:])
                        else:
                            raise AttributeError("X must be provided if 'DataUploaded' is set to False")
                headers_str = '\t'.join(headers)
                samples = X
                neighbors_final=[]
                if samples.shape[0]> 0:
                    failed_queries=0
                    for samp in samples:
                        sample_str = '\t'.join([str(s) for s in samp])
                        queryObject_url = self.base_cloud_url + '/queryVisualization'            
                        if version:
                            query_data = {"instanceName" : self.instanceName,
                                          "version" : version,
                                          "query" : headers_str + '\n' + sample_str,
                                          "authorization" : self.filepassword
                                    }
                        else:
                            query_data = {"instanceName" : self.instanceName,
                                          "query" : headers_str + '\n' + sample_str,
                                          "authorization" : self.filepassword
                                    }              
                        resp_query = requests.post(queryObject_url,data = query_data, auth = (self.username, self.b64password))
                        
                        if resp_query.status_code == 200:
                            ## Converting response to JSON object
                            resp_query_json = json.loads(resp_query.content.decode())
                            
                            ## Extracting neighbors for each class, sorting by distance 
                            ## in ascending order regardless of class
                            neighbors_dict={}
                            for class_ in resp_query_json['listMap'].keys():
                                distance_l=[]
                                id_l=[]
                                for neighbor in resp_query_json['listMap'][class_]['queryRelatedObject']:
                                    distance = neighbor['distance']
                                    objectId = neighbor['objectId']
                                    distance_l.append(distance)
                                    id_l.append(objectId)
                                neighbors = [(id_0,float(dist)) for dist,id_0 in sorted(zip(distance_l,id_l),reverse=False)]
                                neighbors_dict[class_] = neighbors
                            neighbors_final.append(neighbors_dict)
                        else:
                            failed_queries += 1
                            error_message = resp_query.content.decode()
                            
                    if not failed_queries:
                        return neighbors_final
                    else:
                        raise AttributeError("One or more queries producing errors. API error message: " + error_message + ".")
                else:
                    raise AttributeError("Must contain both headers and query objects for prediction.")           
            else:
                raise AttributeError("Must create instance by using fit() before predicting.")
        else:
            raise AttributeError("Currently, the get_neighbors() functionality only exists for Leliel angels.")
            
            
    def get_factors(self, X, *, version = ''):
        """
        Returns local "Why" factors for each prediction.
        
        Parameters
        ----------
        X: {array-like}. Samples to predict. shape = (n_samples, n_features). 
        First line must be headers. 
        
        Returns
        ----------
        y_factors: array, shape = (n_samples,(n_features,3)
        Feature/value pairs, predictive weights, and boolean variable depicting if 
        feature/value pair is similar to the query object or not. This is 
        provided for each sample prediction in X.
        """
        if self.angel.lower() == 'leliel':
            if self.instanceName:
                if isinstance(X,pd.DataFrame):
                    headers = list(X.columns)
                    X = np.asarray(X)
                elif isinstance(X,pd.Series):
                    headers = [X.name]
                    X = np.asarray(X)
                else: 
                    if type(X) == str:
                        raise TypeError('X cannot be a string. Acceptable types: pandas Dataframe, Series or numpy array.')
                    else:
                        if len(X) > 0:
                            headers = list(X[0])
                            X = np.asarray(X[1:])
                        else:
                            raise AttributeError("X must be provided if 'DataUploaded' is set to False")
                headers_str = '\t'.join(headers)
                samples = X
                y_factors=[]
                if samples.shape[0]> 0:
                    failed_queries = 0
                    for samp in samples:
                        sample_str = '\t'.join([str(s) for s in samp])
                        queryVisualization_url = self.base_cloud_url + '/queryVisualization'            
                        if version:
                            query_data = {"instanceName" : self.instanceName,
                                          "version" : version,
                                          "query" : headers_str + '\n' + sample_str,
                                          "authorization" : self.filepassword
                                    }
                        else:
                            query_data = {"instanceName" : self.instanceName,
                                          "query" : headers_str + '\n' + sample_str,
                                          "authorization" : self.filepassword
                                    }              
                        resp_query = requests.post(queryVisualization_url,data = query_data, auth = (self.username, self.b64password))
                                   
                        if resp_query.status_code == 200:
                            ## Converting response to JSON object
                            resp_query_json = json.loads(resp_query.content.decode())
                            predicted_class = resp_query_json['rawQueryResponse']['winnerUsingThreshold']['predictedClass']
                            
                            ## Loop through query response, extract feature value pairs 
                            ## along with their local weights for predicted class
                            feature_value_pairs=[]
                            weights=[]
                            similar_to_query=[]
                            for item in resp_query_json['listMap'][predicted_class]['globalQueryObjects']:
                                feature_value_pairs.append(item['matchedItem'])
                                weights.append(float(item['weight']))
                                similar_to_query.append(item['similarToQuery'])
                            y_factors.append(list(zip(feature_value_pairs,weights,similar_to_query)))
                        else:
                            failed_queries += 1
                            error_message = resp_query.content.decode()
                            
                    if not failed_queries:
                        return y_factors
                    else:
                        raise AttributeError("One or more queries producing errors. API error message: " + error_message + ".")
                else:
                    raise AttributeError("Must contain both headers and query objects for prediction.")           
            else:
                raise AttributeError("Must create instance by using fit() before predicting.")
        else:
            if self.instanceName:
                if isinstance(X,pd.DataFrame):
                    headers_list = list(X.columns)
                    X = np.asarray(X)
                elif isinstance(X,pd.Series):
                    headers_list = [X.name]
                    X = np.asarray(X)
                else: 
                    if type(X) == str:
                        raise TypeError('X cannot be a string. Acceptable types: pandas Dataframe, Series or numpy array.')
                    else:
                        if len(X) > 0:
                            headers_list = list(X[0])
                            X = np.asarray(X[1:])
                        else:
                            raise AttributeError("X must be provided if 'DataUploaded' is set to False")
                samples = X
                y_factors=[]
                if samples.shape[0]> 0:
                    failed_queries = 0
                    for samp in samples:
                        data_dict = {}
                        for i,col in enumerate(headers_list):
                            data_dict[col] = samp[i]
                        queryFactors_url = self.base_v2_url + '/queryFactors'
                        if version:
                            query_data = {"instanceName" : self.instanceName,
                                          "version" : version,
                                          "query" : data_dict,
                                          "authorization" : self.filepassword
                                    }
                        else:
                            query_data = {"instanceName" : self.instanceName,
                                          "query" : data_dict,
                                          "authorization" : self.filepassword
                                    }
                        headers_api = {'Content-type': 'application/json'}
                        resp_query = requests.post(queryFactors_url,data = json.dumps(query_data), auth = (self.username, self.b64password),headers = headers_api)
                         
                        if resp_query.status_code == 200:
                            ## Converting response to JSON object
                            resp_query_json = json.loads(resp_query.content.decode())
                            
                            ## Loop through query response, extract feature value pairs 
                            ## along with their local weights
                            feature_value_pairs=[]
                            weights=[]
                            similar_to_query=[]
                            for item in resp_query_json['featuresContribution']:
                                feature_value_pairs.append(item['colName']+'/'+str(item['value']))
                                weights.append(float(list(item['contributionByClass'].values())[0]))
                                similar_to_query.append(item['similarToQuery'])
                            y_factors.append(list(zip(feature_value_pairs,weights,similar_to_query)))
                        else:
                            failed_queries += 1
                            error_message = resp_query.content.decode()
                    if not failed_queries:
                        return y_factors
                    else:
                        raise AttributeError("One or more queries producing errors. API error message: " + error_message + ".")              
                else:
                    raise AttributeError("Must contain both headers and query objects for prediction.")           
            else:
                raise AttributeError("Must create instance by using fit() before predicting.")