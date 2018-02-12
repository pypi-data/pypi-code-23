"""
    Fitchain connector - Fitchain SDK 

    Client application to connect to the fitchain API
    Compatible with Python2,2.7,3.x

    :copyright: (c) 2017 fitchain.io
"""

import requests
from fitchain import dummy_data as dd


#import json
# from requests.auth import HTTPBasicAuth
# import pandas as pd
# import numpy as np
# import os, io
# import magic  # automatic detection of filetype
# from StringIO import StringIO  #obsolete
# from io import StringIO


class FitchainConnector:
    def __init__(self, token=None, verbose=False):
        self.credentials = {}
        self.API_BASE     = "http://localhost:9400/v1" 
        self.__request_headers = {} # {"Authorization":"Bearer " + self.token}
        self.namespace     = '' #'daan'
        self.EP_LOGIN      = '/login'    # not used
        self.EP_LOGOUT     = '/logout'   # not used
        self.EP_PROJECTS   = '/projects'
        self.EP_WORKSPACE  = '/workspaces'   # GET/POST/PUT/DEL (json schema)
        self.EP_DATA       = '/data'
        self.EP_DATASOURCE = '/datasources'
        self.EP_PROVIDER   = '/providers'
        self.EP_DATA_CRED  = '/data/credentials'
        self.EP_JOBS       = '/jobs'
        self.EP_STATUS     = '/gateway'
        self.verbose       = verbose
        
        
    def _url(self, path):
        return self.API_BASE + path # +'/' + self.namespace
    
    def status(self):
        url = self._url(self.EP_STATUS)
        r = requests.get(url, headers=self.__request_headers)
        if self.verbose:
            print('GET', r.url)

        return r.json()
        
    def get_projects(self, fields=None):
        """ GET v1/projects 
        
        :fields: dict <optional>
        
        eg.
        fields = {'key1': 'value1', 'key2': 'value2'}
        GET http://localhost/projects?key2=value2&key1=value1
        """
        url = self._url(self.EP_PROJECTS)
        r = requests.get(url, params=fields, headers=self.__request_headers)
        print('from get_projects', r)
        
        if self.verbose:
            print('GET', r.url)
        
        return r.json()

    def get_project(self, project_id):
        url = self._url(self.EP_PROJECTS+'/{:s}'.format(project_id))
        
        if self.verbose:
            print('GET', url)
        r = requests.get(url, headers=self.__request_headers)
        print('from get_project', r)
        # TODO check there is json method
        return r.json()

    def add_provider(self, p_name, p_type, p_config, p_id):
        """ 
        :p_name: str 
        :p_type: str
        :config: dict
        :p_id: str
        
        """
        
        headers = {'Content-Type' : 'application/json'}
        payload = {
            'name'  : str(p_name),
            'type'  : str(p_type),
            'config': p_config,
            'id': str(p_id)
        }
        
        url = self._url(self.EP_PROVIDER)
        print('add_provider', url, payload)
        
        return requests.post(url, headers=headers, json=payload)


    def add_datasource(self, d_provider, d_config, d_name, d_description, d_format, d_id):
        headers = {'Content-Type' : 'application/json'}
        payload = {
            'provider' : str(d_provider),
            'config' : d_config,
            'name' :str(d_name),
            'description' : str(d_description),
            'format': str(d_format),
            'id': str(d_id)
        }
        url = self._url(self.EP_DATASOURCE)
        print('add_datasource', url, payload)    
        r = requests.post(url, headers=headers, json=payload)
        return r.json()

    def get_workspace(self, workspace_id):
        url = self._url(self.EP_WORKSPACE+'/{:s}'.format(workspace_id))
        
        if self.verbose:
            print('GET', url)
            
        r = requests.get(url, headers=self.__request_headers)
        #print('from get_workspace', type(r.text), len(r.text))
        if len(r.text) == 0:
            return None
        
        return r.json()

    
    def add_workspace(self, project_id, workspace_id, sourcecode):
        headers = {'Content-Type' : 'application/json'}
        payload = {
            'project_id' : str(project_id),
            'id' : str(workspace_id),
            'sourcecode' : sourcecode
        }
        url = self._url(self.EP_WORKSPACE)
        print('add_workspace', url, payload)    
        
        ws_exist = self.get_workspace(workspace_id)
        print('DEBUG from add_workspace ws_exist=', ws_exist)
        if not ws_exist:
            r = requests.post(url, headers=headers, json=payload)
            print('DEBUG from add_workspace', r)
            return r.json()
        # else PUT
        # TODO 
    
    
    def get_providers(self):
        url = self._url(self.EP_PROVIDER)

        if self.verbose:
            print('from get_providers', 'GET', url)
        r = requests.get(url, headers=self.__request_headers)
        return r.json()
    
        
    def get_provider(self):
        pass
    
    def get_jobs(self):
        url = self._url(self.EP_JOBS)

        if self.verbose:
            print('GET', url)
        return requests.get(url, headers=self.__request_headers)

    def get_job(self, job_id):
        url = self._url(self.EP_JOBS+'/{:d}'.format(job_id))
        if self.verbose:
            print('GET', url)
        return requests.get(url, headers=self.__request_headers)
    
    
    def load_data(self, project_id):
        my_project = self.get_project(str(project_id))
        my_schema = my_project['datasources'][0]['schema']
        dummy = dd.DummyData(my_schema)
        df = dummy.generate_data()
        return df

    
    def validate(self):
        pass
    
    
    """
    def submit_model(self, name, description, mimetype, size, location_url):
        data =  {
            'name'        : name,
            'description' : description,
            'mimetype'    : mimetype,
            'filesize'    : size,
            'location_url': location_url,
        }
        return requests.post(self._url('/model'), json=data)
       
    def create_job(self, name, description, data, model, public):
        url = self._url('/jobs')
        payload = {
            'name'        : name,
            'description' : description,
            'data'   : data,
            'model'  : model,
            'public' : public,
        }
        return requests.post(url, headers=self.__request_headers, json=payload)
    """

    
    """
    def search_datasource(self, params):
        url = self._url('/datasources'+str(params))
        print('Searching...%s'%url)
        return requests.get(url, headers=self.__request_headers)

    def add_task(self, summary, description=""):
        return requests.post(self._url('/tasks/'),
                            json={
                                'summary': summary,
                                'description': description,
                                })

    def delete_task(self, task_id):
        return requests.delete(self._url('/tasks/{:d}/'.format(task_id)))

    def update_task(self, task_id, summary, description):
        url = self._url('/tasks/{:d}/'.format(task_id))
        return requests.put(url, json={
                            'summary': summary,
                            'description': description,
                            })
    
    def __datasource_getinfo(self, localpath, holdout=True):
        # Private method (CSV supported)
        # TODO: excel, ...
        # Requires pip install python-magic
        # Return fileinfo and holdout subset (dataframe)
        
        #mimetype = magic.from_file(localpath, mime=True)

        col_types = []
        col_values = []
        info = {}
        holdout_set = None

        try:
            data = pd.read_csv(localpath, index_col=0) # header = None
            info['size'] = 1./1024*os.stat(localpath).st_size # size in kB
            info['filetype'] = 'csv'
            col_names = data.columns        # column names
            row_num, col_num = data.shape   # data shape (rows,cols)
            print('data shape', data.shape)

        except:
            print('File format not recognized (Try with csv, excel, txt)')
            return False, False

        # Collect stats of original data
        for y in col_names:
            if(data[y].dtype == np.float64 or data[y].dtype == np.int64):
                  col_types.append('n')
            else:
                  col_types.append('s')

            # Unique values per column
            vals = len(set(data[y]))
            col_values.append(vals)

        # Prepare holdout set
        # TODO let's get rid of this with container authentication and verification
        # at data provider side
        if holdout:
            holdout_set = data.sample(frac=0.1, replace=False)
            #print('holdoutset shape', holdout_set.shape)
            #print(holdout_set.head())

        # create data structure to post
        info['column_names']  = '|'.join(str(e) for e in col_names)
        info['column_types']  = '|'.join(str(e) for e in col_types)
        info['column_values'] = '|'.join(str(e) for e in col_values)
        info['num_columns']   = data.shape[1]

        return holdout_set,info

    
    def post_datasource(self, name, description, sourcepath=None, remote=False):
        # Post file at localpath (raw data) or file at remotepath (S3 supported)
        
        url = self._url(self.EP_DATASOURCE)

        files = None  # we never upload files content
        holdout_set = None

        # datasource is local
        if sourcepath and not remote:
            #files = {'file': open(sourcepath,'rb')}    # send raw file content

            # Prepare holdout set and send
            holdout_set, info = self.__datasource_getinfo(sourcepath)

            if holdout_set is not None and info:
                print('content info to buf')
                s_buf = StringIO()
                holdout_set.to_csv(s_buf)
                s_buf.seek(0)

                # transfer raw content as csv file
                files = {'file': s_buf.getvalue()} #.decode()}
                #files = {'file': open(s_buf, 'rb')} #'./pippo.csv','rb')}

                # add other fields
                info['location_url'] = 'local'
                info['name'] = name
                info['description'] = description
            elif holdout_set is None:
                print('Cannot extract holdout set')
                return False

        # datasource is remote
        if sourcepath and remote:
            # if data are on S3 send the URL
            values['location_url'] = sourcepath
            pass
            #TODO s3io get from S3 url
        print(info)
        return requests.post(url, files=files, data=info,
                              auth=HTTPBasicAuth(self.credentials['username'], self.credentials['password']))
    
    def get_models(self):
        url = self._url(self.EP_MODELS)
        return requests.get(url,
                            auth=HTTPBasicAuth(self.credentials['username'], self.credentials['password']))

    def get_model(self, params):
        url = self._url(self.EP_MODELS+params)
        return requests.get(url,
                            auth=HTTPBasicAuth(self.credentials['username'], self.credentials['password']))

    def submit_model(self, name, description, mimetype, size, location_url):
        return requests.post(self._url('/model'),
                             auth=HTTPBasicAuth(self.credentials['username'], self.credentials['password']),
                            json={
                                'name'        : name,
                                'description' : description,
                                'mimetype'    : mimetype,
                                'filesize'    : size,
                                'location_url': location_url,
                                })

    def post_model(self, model):
        print('Sending %s to remote party'%model)

    def deploy_model(self, model):
        url = self._url(self.EP_PROJECTS+'/{:d}'.format(model))
        json_model = model.model
        return requests.post(url, json=json_model,
                              auth=HTTPBasicAuth(self.credentials['username'], self.credentials['password']))

    """

# TODO rename this as FitchainConnector.py
# TODO create test file
# TODO create fitchain-blockchain-client
# TODO write Readme and upload to public Fitchain github

"""
def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))
"""

"""
with requests.Session() as s:
    p = requests.post(API_BASE + EP_LOGIN, json=login_json)

    if p.status_code != 200:
        # This means something went wrong.
        raise ApiError('POST /login {}'.format(p.status_code))

    # print the html returned or something more intelligent to see if it's a successful login page.
    print p.text

    # An authorised request.
    r = s.get(base_api + endpoint_projects, auth=HTTPBasicAuth(login_json['username'], login_json['password']))
    print r.text
"""
# https://realpython.com/blog/python/api-integration-in-python/

###
### #> fc projects list
### #> fc project show <id>
### #> fc model create <project_id>

### Do awesome stuff in python

### #> fc model train <your-python-file>

if __name__ == "__main__":
    """
    conn = FitchainConnector(verbose=True)
    ### #> fc projects list
    projects = conn.get_projects()
    awesome_project_id = projects[2].id

    ### #> fc project show <id>
    project = conn.get_project(awesome_project_id)

    ### #> fc model create <project_id>
    working_copy = conn.create_working_copy(awesome_project_id)
    """
    
    conn = FitchainConnector(verbose=True)
    projects = conn.get_projects()
    print('Get projects')
    print('Found', len(projects), 'projects')
    for p in projects:
        p_id = p['id']
        proj_desc = conn.get_project(project_id = p_id)
        print('\n', proj_desc)

    # get the project id to work on 
    my_project = projects[2]
    my_project_id = my_project['id']
    data = conn.load_data(project_id=my_project_id)
    
    

    



















    
    print('\n\nAdding provider')
    config = {'path': '/Users/frag/Documents/data'}
    ret = conn.add_provider(p_name='frags space',
                            p_type='local',
                            p_config= config,
                            p_id = 'yet_another_frag_local')
    print('add_provider', ret)
    
    print('\n\n')
    providers = conn.get_providers()
    for p in providers:
        print(p['id'], p['type'])


    print('Adding datasource')
    provider_id = 'frag_local'
    config = {'path': 'Regions-phenotype105K.csv'}
    ret = conn.add_datasource(d_provider= provider_id,
                              d_config=config,
                              d_name='pheno_105',
                              d_description='phenotypes of people with mental disorders',
                              d_format='csv',
                              d_id='frag_pheno_105')


    print(ret)
