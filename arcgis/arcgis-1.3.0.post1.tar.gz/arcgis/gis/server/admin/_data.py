"""
This resource provides information about the data holdings of the
server. This information is used by ArcGIS for Desktop and other
clients to validate data paths referenced by GIS services.
You can register new data items with the server by using the
Register Data Item operation. Use the Find Data Items operation to
search through the hierarchy of data items.
The Compute Ref Count operation counts and lists all references to a
specific data item. This operation helps you determine if a
particular data item can be safely deleted or refreshed.
"""
from __future__ import absolute_import
import os
import re
import json
from .._common import BaseServer
from .._common.util import contextmanager, _tempinput
########################################################################
class DataStoreManager(BaseServer):
    """
    This resource provides information about the data holdings of the
    server, as well as the ability to manage (add new items, update primary 
    data store, remove a data store item, etc) the data store. Data items 
    are used by ArcGIS for Desktop and other clients to validate data paths 
    referenced by GIS services.

    .. note::
        A relational data store type represents a database platform that has been 
        registered for use on a portal's hosting server by the ArcGIS Server 
        administrator. Each relational data store type describes the
        properties ArcGIS Server requires in order to connect to an instance of
        a database for a particular platform. At least one registered
        relational data store type is required before client applications such
        as Insights for ArcGIS can create Relational Database Connection portal
        items.

       
    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    url                    Required string. The URL to the Data Store URL.
    ------------------     --------------------------------------------------------------------
    gis                    Optional string. The GIS, Server, or ServicesDirectory object.
    ==================     ====================================================================
        
    """
    _con = None
    _json_dict = None
    _url = None
    _json = None
    _gis = None
    _datastores = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 gis=None,
                 **kwargs):
        """Constructor
            Inputs:
               url - admin url
               gis - gis object
               initialize - optional initializes the componenents in the class
        """
        connection = kwargs.pop('connection', None)
        initialize = False
        super(DataStoreManager, self).__init__(
            gis=gis,
            url=url)
        if hasattr(gis, '_con'):
            self._con = gis._con
        elif hasattr(gis, 'post'):
            self._con = gis
        if connection:
            self._con = connection
        self._url = url
        if initialize:
            self._init()
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s for %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s for %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def list(self):
        """Retrieves a list of datastore objects.
        
        :return:
           The list of datastore items.
        """
        self._datastores = None
        if self._datastores is None:
            self._datastores = []
            for item in self.items['rootItems']:
                for path in self.search(parent_path=item)['items']:
                    self._datastores.append(Datastore(datastore=self,
                                                      path=path['path'],
                                                      datadict=None))
        return self._datastores
    #----------------------------------------------------------------------
    @property
    def config(self):
        """
           Gets the data store configuration properties. These properties 
           affect the behavior of the data holdings of the server. For
           example, the blockDataCopy property - when this property is false, 
           or not set at all, copying data to the site when publishing services 
           from a client application is allowed. This is the default behavior. 
           When this property is true, the client application is not allowed to 
           copy data to the site when publishing. Rather, the publisher is
           required to register data items through which the service being
           published can reference data. Values: true | false
        """
        
        """ jenn note -- need link or list of the possible data store configuration properties."""
        params = {
            "f" : "json"
        }
        url = self._url + "/config"
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    @config.setter
    def config(self, config):
        """
        This operation allows you to update the data store configuration
        You can use this to allow or block the automatic copying of data
        to the server at publish time
           
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        config                 Required string. A JSON string containing the data store configuration.
        ==================     ====================================================================

        :return:
           JSON dictionary of the set configuration properties.

        """
        if config is None:
            config = {}
        params = {
            "f" : "json",
            "datastoreConfig" : config
        }
        url = self._url + "/config/update"
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def get(self, path):
        """
        Retrieves the data item object at the given path.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        path                   Required string. The path to the data item.
        ==================     ====================================================================


        :return:
            The data item object, None if not found.
        """
        if path[0] != "/":
            path = "/%s" % path
        params = {"f" : "json"}
        urlpath = self._url + "/items" + path

        datadict = self._con.post(urlpath, params)
        if 'status' not in datadict:
            return Datastore(self, "/items" + path, datadict)
        else:
            return None
    #----------------------------------------------------------------------
    def add_folder(self,
                   name,
                   server_path,
                   client_path=None):
        """
        Registers a folder with the data store.

            
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        name                   Required string. The unique fileshare name on the server.
        ------------------     --------------------------------------------------------------------
        server_path            Required string. The path to the folder from the server (and client, if shared path).
        ------------------     --------------------------------------------------------------------
        client_path            Optional string. If folder is replicated, the path to the folder from 
                               the client; if folder is shared, don't set this parameter.
        ==================     ====================================================================
        
        :return:
            The data item if successfully registered, None otherwise.

        """
        conn_type = "shared"
        if client_path is not None:
            conn_type = "replicated"

        item = {
            "type" : "folder",
            "path" : "/fileShares/" + name,
            "info" : {
                "path" : server_path,
                "dataStoreConnectionType" : conn_type
            }
        }
        if client_path is not None:
            item['clientPath'] = client_path
        res = self._register_data_item(item=item)
        if res['status'] == 'success' or res['status'] == 'exists':
            return Datastore(self, "/fileShares/" + name)
        else:
            return None
        return
    #----------------------------------------------------------------------
    def add(self,
            name,
            item):
        """
        Registers a new data item with the data store.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        name                   Required string. The name of the new data item.
        ------------------     --------------------------------------------------------------------
        item                   Required string. The dictionary representing the data item. 
                               See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000001s9000000
        ==================     ====================================================================
        

        :return:
            The data item if registered successfully, None otherwise.
        """
        res = self._register_data_item(item=item)
        if res['status'] == 'success' or res['status'] == 'exists':
            return Datastore(self, "/enterpriseDatabases/" + name)
        else:
            #print(str(res))
            return None
    #----------------------------------------------------------------------
    def add_bigdata(self,
                    name,
                    server_path=None):
        """
        Registers a bigdata fileshare with the data store.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        name                   Required string. The unique bigdata fileshare name on the server.
        ------------------     --------------------------------------------------------------------
        server_path            Optional string. The path to the folder from the server.
        ==================     ====================================================================
        
        :return:
            The data item if successfully registered, None otherwise.
        """
        output = None
        pattern = r'\\\\[a-zA-Z]+'
        if re.match(pattern, server_path) is not None:  # starts with double backslash, double the backslashes
            server_path = server_path.replace('\\', '\\\\')

        path_str = '{"path":"' + server_path + '"}'
        params = {
            'f': 'json',
            'item' : json.dumps({
                "path": "/bigDataFileShares/" + name,
                "type": "bigDataFileShare",

                "info": {
                    "connectionString": path_str,
                    "connectionType": "fileShare"
                }
            })
        }
        res = self._register_data_item(item=params)

        if res['status'] == 'success' or res['status'] == 'exists':
            output = Datastore(self, "/bigDataFileShares/" + name)
        return output
    #----------------------------------------------------------------------
    def add_database(self,
                     name,
                     conn_str,
                     client_conn_str=None,
                     conn_type="shared"):
        """
        Registers a database with the data store.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        name                   Required string. The unique database name on the server.
        ------------------     --------------------------------------------------------------------
        conn_str               Required string. The path to the folder from the server (and client, 
                               if shared or serverOnly database)
        ------------------     --------------------------------------------------------------------
        client_conn_str        Optional string. The connection string for client to connect to replicated enterprise database>
        ------------------     --------------------------------------------------------------------
        conn_type              Optional string. The connection type.  Default value is shared, 
                               other choices are replicated or serverOnly
        ==================     ====================================================================
        

        :return:
            The data item if successfully registered, None otherwise.
        """

        item = {
            "type" : "egdb",
            "path" : "/enterpriseDatabases/" + name,
            "info" : {
                "connectionString" : conn_str,
                "dataStoreConnectionType" : conn_type
            }
        }

        if client_conn_str is not None:
            item['info']['clientConnectionString'] = client_conn_str

        is_managed = False
        if conn_type == "serverOnly":
            is_managed = True

        item['info']['isManaged'] = is_managed
        res = self._register_data_item(item=item)
        if res['status'] == 'success' or res['status'] == 'exists':
            return Datastore(self, "/enterpriseDatabases/" + name)
        else:
            return None
        return
    #----------------------------------------------------------------------
    def get_total_refcount(self, path):
        """
        The total number of references to a given data item
        that exists on the server. You can use this operation to
        determine if a data resource can be safely deleted, or taken
        down for maintenance.
           
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        path                   Required string. The complete hierarchical path to the item.
        ==================     ====================================================================
           

        :return:
            A JSON dictionary containing a number representing the total count.
    
        """
        url = self._url + "/computeTotalRefCount"
        params = {
            "f" : "json",
            "path" : path
        }
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def make_datastore_machine_primary(self,
                                       item_name,
                                       machine_name):
        """
        Promotes a standby machine to the primary Data Store machine. The
        existing primary machine is downgraded to a standby machine.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        item_name              Required string. The primary machine item name in the data store. 
        ------------------     --------------------------------------------------------------------
        machine_name           Required string. The machine name of the machine to promote to primary.
        ==================     ====================================================================
        

        :return:
            A boolean indicating success (True) or failure (False).

        """
        url = self._url + "/items/enterpriseDatabases" + \
            "/{datastoreitem}/machines/{machine_name}/makePrimary".format(
                datastoreitem=item_name,
                machine_name=machine_name)
        params = {"f" : "json"}

        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def get_relational_datastore_type(self, type_id):
        """
        This resource lists the properties of a registered relational data
        store of the given type. The properties returned are those that client
        applications must provide when creating a Relational Database
        Connection portal item.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        type_id                Required string. The datastore type ID of interest. 
                               See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Relational_Data_Store_Types/02r300000303000000/ 
        ==================     ====================================================================


        :return:
           A JSON string listing the properties 
           
        """
        """ jenn note: useful would be a list of possible datastore type IDs -- ??? esri.teradata, esri.sqlserver, esri.hana """ 
        
        params = {"f" : "json"}
        url = self._url + "/relationalDatastoreTypes/{i}".format(
            i=type_id)
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    @property
    def relational_datastore_types(self):
        """
        Gets a list of the relational data store types that have been
        registered with the server. Each registered relational data store
        type has both an id and a name property, as well as an array of
        userDefinedProperties, which indicates the properties client
        applications must provide when creating a Relational Database
        Connection portal item. Only administrators can register and
        unregister a relational data store type. The following database
        platforms are supported: SAP HANA, Microsoft SQL Server and
        Teradata.
        """
        params = {"f" : "json"}
        url = self._url + "/relationalDatastoreTypes"
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def search(self,
               parent_path=None,
               ancestor_path=None,
               types=None,
               id=None):
        """
        Use this operation to search through the various data items that are registered in the server's data store.
           
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        parent_path            Optional string. The path of the parent under which to find items.
        ------------------     --------------------------------------------------------------------
        ancestor_path          Optional string. The path of the ancestor under which to find items.
        ------------------     --------------------------------------------------------------------
        types                  Optional string. A filter for the type of the items (for example, fgdb or folder or egdb).
        ------------------     --------------------------------------------------------------------
        id                     Optional string. A filter to search by the ID of the item.
        ==================     ====================================================================
        
        
        :return:
            A JSON list of the items found matching the search criteria.
        """
        
        """ jenn note: list of possible types """
        params = {
            "f" : "json",
        }
        if parent_path is not None:
            params['parentPath'] = parent_path
        if ancestor_path is not None:
            params['ancestorPath'] = ancestor_path
        if types is not None:
            params['types'] = types
        if id is not None:
            params['id'] = id
        url = self._url + "/findItems"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def _register_data_item(self, item):
        """
        Registers a new data item with the server's data store.
           
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        item                   Required string. The JSON representing the data item. 
                               See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000001s9000000
        ==================     ====================================================================
        
        :return:
            A response
        """
        params = {
            "item" : item,
            "f" : "json"
        }
        url = self._url + "/registerItem"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    @property
    def data_items(self):
        """
        Gets the list of data items that are the root of all other data items in the data store.
        """
        url = self._url + "/items"
        params = {
            "f" : "json"
        }
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def validate(self):
        """
        Validates all the items in the data store.
        
        :return:
            True if all items are valid.
        """
        params = {
            "f" : "json"
        }
        url = self._url + "/validateAllDataItems"
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def make_primary(self, datastore_name, machine_name):
        """
        Promotes a standby machine to the primary Data Store machine. The
        existing primary machine is downgraded to a standby machine.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        datastore_name         Required string. The primary machine name in the data store.
        ------------------     --------------------------------------------------------------------
        machine_name           Required string. The machine name of the machine to promote to primary.
        ==================     ====================================================================
        

        :return:
            A boolean indicating success (True) or failure (False).

        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/makePrimary" % (datastore_name, machine_name)
        params = {
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def remove_datastore_machine(self, item_name, machine_name):
        """
        Removes a standby machine from the Data Store. This operation is
        not supported on the primary Data Store machine.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        item_name              Required string. The standby machine item name in the data store. 
        ------------------     --------------------------------------------------------------------
        machine_name           Required string. The machine name of the machine to remove.
        ==================     ====================================================================

        :return:
            A boolean indicating success (True) or failure (False).

        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/remove" % (item_name, machine_name)
        params = {
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def start(self, item_name, machine_name):
        """
        Starts the database instance running on the Data Store machine.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        item_name              Required string. The database item name in the data store to start. 
        ------------------     --------------------------------------------------------------------
        machine_name           Required string. The machine name of the machine with the database 
                               instance to start.
        ==================     ====================================================================

        :return:
           A boolean indicating success (True) or failure (False).
        
        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/start" % (item_name, machine_name)
        params = {
            "f": "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def stop(self, item_name, machine_name):
        """
        Stop the database instance running on the Data Store machine.

       
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        item_name              Required string. The database item name in the data store to stop. 
        ------------------     --------------------------------------------------------------------
        machine_name           Required string. The machine name of the machine with the database 
                               instance to stop.
        ==================     ====================================================================

        :return:
           A boolean indicating success (True) or failure (False).
        
        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/stop" % (item_name,
                                                                              machine_name)
        params = {
            "f": "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def _unregister_data_item(self, path):
        """
        Unregisters a data item that has been previously registered with
        the server's data store.


        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        path                   Required string. The path to the share folder.
        ==================     ====================================================================

        :return:
            T
            
            .. code-block:: python
        
            EXAMPLE:
            
            path = r"/fileShares/folder_share"
            print data.unregisterDataItem(path)
            
        """
        url = self._url + "/unregisterItem"
        params = {
            "f" : "json",
            "itempath" : path
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def validate_egdb(self, data_store_name, name):
        """
        Checks the status of the given ArcGIS Data Store and provides a health check response.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        data_store_name        Required string. The item name of the data store. 
        ------------------     --------------------------------------------------------------------
        name                   Required string. The machine name of where the data store is.
        ==================     ====================================================================

        :return:
            A JSON response containing general status information and an overall health report.
            
        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/validate" % (data_store_name,
                                                                                  name)
        params = {
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
###########################################################################
class Datastore(BaseServer):
    """
    Represents a single Datastore in the Data Store Manager.


    """
    _path = None
    _datastore = None
    _json_dict = None
    _json = None
    _con = None
    _url = None
    def __init__(self, datastore, path, datadict=None, **kwargs):
        self._path = path

        super(Datastore, self).__init__(datastore=datastore,
                                        path=path,
                                        url=datastore._url + "%s" % path,
                                        connection=datastore._con,
                                        initialize=True,
                                        datadict=datadict)
        path = "/items%s" % path
        if datastore:
            self._con = datastore._con
        self._datastore = datastore
        self._url = "%s%s" % (datastore._url, path)
        self._init()
    #----------------------------------------------------------------------
    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self._json_dict.items()]
        return '\n'.join(state)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s title:"%s" type:"%s">' % (type(self).__name__, self._url, self.type)
    #----------------------------------------------------------------------
    @property
    def manifest(self):
        """
        Gets the manifest resource for a big data file share.
        """
        data_item_manifest_url = self._url + "/manifest"
        if data_item_manifest_url.find('/bigDataFileShares') != -1:
            params = {
                'f': 'json',
            }
            res = self._con.post(data_item_manifest_url,
                                 params,
                                 verify_cert=False)
        else:
            res = {}
        return res
    #----------------------------------------------------------------------
    @manifest.setter
    def manifest(self, value):
        """
        Sets the manifest resource for a big data file share.
        """
        manifest_upload_url =  self._url + '/manifest/update'
        if manifest_upload_url.find('/bigDataFileShares') != -1:
            with _tempinput(json.dumps(value)) as tempfilename:
                # Build the files list (tuples)
                files = []
                files.append(('manifest', tempfilename, os.path.basename(tempfilename)))

                postdata = {
                    'f' : 'pjson'
                }

                resp = self._.con.post(manifest_upload_url, postdata, files, verify_cert=False)
                if resp['status'] == 'success':
                    return True
                else:
                    return False
        else:
            return None
    #---------------------------------------------------------------------
    @property
    def hints(self):
        """
        Gets the hints resource for a big data file share. Hints
        are advanced parameters to control the generation of a manifest.
        """
        params = {
            'download' : True,
            'read' : True
        }
        url = self._url + "/hints"
        return self._con.get(path=url,
                             params=params)
    #---------------------------------------------------------------------
    @hints.setter
    def hints(self,
              hints):
        """
        Sets the hints resource for a big data file share. Hints
        are advanced parameters to control the generation of a manifest.
        
        Upload a hints file for a big data file share item. This will
        replace the existing hints file. To apply the control parameters in
        the hints file and regenerate the manifest, use the editDataItem to
        edit the big data file share (using the same data store item as
        input) which will regenerate the manifest. When a manifest is
        regenerated, it will be updated only for datasets that have hints
        and for new datasets that are added to the existing big data file
        share location.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        name                   Required string. The name of the big data item to update.
        ------------------     --------------------------------------------------------------------
        hints                  Required string. The hints file to be uploaded.
        ==================     ====================================================================

        """
        params = {
            "f" : "json"
        }
        files = {"hints" : hints}

        url = self._url + "/hints/update"
        if url.find('/bigDataFileShares') == -1:
            return None
        return self._con.post(path=url,
                              files=files,
                              postdata=params)
    #----------------------------------------------------------------------
    @property
    def ref_count(self):
        """
        The total number of references to this data item that exist on the
        server. You can use this property to determine if this data item
        can be safely deleted or taken down for maintenance.
        
        :return:
           A number indictaing the number of references to this data item.
        """
        return self.totalRefCount
    #----------------------------------------------------------------------
    def delete(self):
        """
        Unregisters this data item from the data store.
        
        :return:
           A boolean indicating success (True) or failure (False).
        """
        params = {
            "f" : "json" ,
            "itempath" : self.path,
            "force": True
        }
        path = self._datastore._url + "/unregisterItem"

        resp = self._con.post(path, params, verify_cert=False)
        if resp:
            return resp.get('success')
        else:
            return False
    #----------------------------------------------------------------------
    def update(self, item):
        """
        Edits this data item to update its connection information.
        
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        item                   Required string. The dict representation of the updated item.
        ==================     ====================================================================

        :return:
            True if the data item was successfully updated, False if the update failed.
            
        """
        params = {
            "f" : "json" ,
            "item" : item
        }
        path = self._datastore._url +  "/items" + self.path +  "/edit"

        resp = self._con.post(path, params, verify_cert=False)
        if resp ['status'] == 'success':
            return True
        else:
            return False
    #----------------------------------------------------------------------
    def validate(self):
        """
        Validates that this data item's path (for file shares) or connection string (for databases)
        is accessible to every server node in the site. This is necessary for the data item to be 
        registered and used successfully with the server's data store.

        :return:
            True if the data item was successfully validated.
        """
        params = {
            "f" : "json",
            "item": self._json_dict
        }
        path = self._datastore._url + "/validateDataItem"

        res = self._con.post(path, params, verify_cert=False)
        return res['status'] == 'success'
    #----------------------------------------------------------------------
    @property
    def datasets(self):
        """
        Gets the datasets in the data store (currently implemented for big data file shares).
        """
        data_item_manifest_url = self._url + "/manifest"

        params = {
            'f': 'json'
        }

        try:
            res = self._con.post(data_item_manifest_url, params, verify_cert=False)
            return res['datasets']
        except:
            return None
