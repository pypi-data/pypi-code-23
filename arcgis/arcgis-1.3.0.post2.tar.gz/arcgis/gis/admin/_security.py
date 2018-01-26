"""
Controls the local portal's security settings
"""
from ..._impl.connection import _ArcGISConnection
from .. import GIS
from ._base import BasePortalAdmin
########################################################################
class PasswordPolicy(BasePortalAdmin):
    """
    Manages a GIS Security Policy.  Administrators can view, update or
    reset the site's security policy.
    """
    _gis = None
    _con = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis=None, **kwargs):
        """Constructor"""
        super(PasswordPolicy, self).__init__(url=url,
                                             gis=gis,
                                             **kwargs)
        initialize = kwargs.pop("initialize", False)
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self._init(self._gis)
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def policy(self):
        """gets/sets the current security policy"""
        if self._properties is None:
            self._init()
        return self._properties
    #----------------------------------------------------------------------
    @policy.setter
    def policy(self, value=None):
        """gets/sets the current security policy"""
        url = "%s/update" % self._url
        from ..._impl.common._mixins import PropertyMap
        if value is None:
            value = self.properties['passwordPolicy']
        if isinstance(value, (dict, PropertyMap)):
            value = dict(value)
        else:
            raise ValueError("Input must be a dictionary of PropertyMap")
        params = {"f" : "json",
                  }
        for k,v in value.items():
            params[k] = v
        res = self._con.post(url, params)
        if 'success' in res:
            self._properties = None
            return res['success']
        return res
    #----------------------------------------------------------------------
    def reset(self):
        """
        resets the security policy to the default install settings
        """
        url = "%s/reset" % self._url
        params = {'f' : 'json'}
        res = self._con.post(url, params)
        if 'success' in res:
            return res['success']
        return res
########################################################################
class Security(BasePortalAdmin):
    """
    This resource is an umbrella for a collection of system-wide resources
    for your portal. This resource provides access to the ArcGIS Web
    Adaptor configuration, portal directories, database management server,
    indexing capabilities, license information, and the properties of your
    portal.
    """
    _gis = None
    _con = None
    _url = None
    _oauth = None
    _eu = None
    _eg = None
    _ssl = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis=None, **kwargs):
        """Constructor"""
        super(Security, self).__init__(url=url,
                                       gis=gis,
                                       **kwargs)
        initialize = kwargs.pop("initialize", False)
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self._init(self._gis)
    #----------------------------------------------------------------------
    @property
    def enterpriseusers(self):
        """
        provides access into managing enterprise users
        """
        if self._eu is None:
            url = "%s/users" % self._url
            self._eu = EnterpriseUsers(url=url, gis=self._gis)
        return self._eu
    #----------------------------------------------------------------------
    @property
    def groups(self):
        """provides access to managing Enterprise Groups with Portal"""
        if self._eg is None:
            url = "%s/groups" % self._url
            self._eg = EnterpriseGroups(url=url, gis=self._gis)
        return self._eg
    #----------------------------------------------------------------------
    @property
    def tokens(self):
        """
        This resource represents the token configuration within your
        portal. Use the set on token_config operation to change the
        configuration properties of the token service.
        """
        url = "%s/tokens" % self._url
        params = {"f" : "json"}
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    @tokens.setter
    def tokens(self, value):
        """
        This resource represents the token configuration within your
        portal. Use the set on token_config operation to change the
        configuration properties of the token service.

        Parameters:
         :value: shared key value
        """
        import six
        params = {
            "f" : "json",
            "tokenConfig" : None}
        if isinstance(value, six.string_types):
            params['tokenConfig'] = {"sharedKey": value}
        elif isinstance(value, dict) and \
             "sharedKey" in value:
            params['tokenConfig'] = value
        else:
            raise ValueError("invalid value given")
        url = "%s/tokens/update" % self._url
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    @property
    def oauth(self):
        """
        The OAuth resource contains a set of operations that update the
        OAuth2-specific properties of registered applications in Portal for
        ArcGIS.
        """
        if self._oauth is None:
            url = "%s/oauth" % self._url
            self._oauth = OAuth(url=url, gis=self._gis)
        return self._oauth
    #----------------------------------------------------------------------
    @property
    def config(self):
        """
        The security configuration consists of the identity store
        configuration.
        If your portal will be authenticated through ArcGIS Web Adaptor,
        you must set up your preferred authentication on your web server.
        Use the Update Identity Store operation to configure your portal to
        connect to your enterprise identity provider such as Windows Domain
        or LDAP. By default, Portal for ArcGIS is configured to use the
        built-in store and token-based authentication.
        """
        url = "%s/config" % self._url
        params = {"f" : "json"}
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    @config.setter
    def config(self, value):
        """
        This operation can be used to update the portal's security settings
        such as whether or not enterprise accounts are automatically
        registered as members of your ArcGIS organization the first time
        they accesses the portal.
        The security configuration is stored as a collection of properties
        in a JSON object. The following properties are supported:
         - enableAutomaticAccountCreation
         - disableServicesDirectory
         - defaultRoleForUser (introduced at ArcGIS 10.4)
        The automatic account creation flag (enableAutomaticAccountCreation)
        determines the behavior for unregistered enterprise accounts the
        first time they access the portal. When the value for this property
        is set to false, first time users are not automatically registered
        as members of your ArcGIS organization, and have the same access
        privileges as other nonmembers. For these accounts to sign in, an
        administrator must register the enterprise accounts using the
        Create User operation.
        The default value for the enableAutomaticAccountCreation property
        is false. When this value is set to true, portal will add
        enterprise accounts automatically as members of your ArcGIS
        organization.
        The disableServicesDirectory property controls whether the HTML
        pages of the services directory should be accessible to the users.
        The default value for this property is false, meaning the services
        directory HTML pages are accessible to everyone.
        Use the defaultRoleForUser property to set which role the portal
        automatically assigns to new member accounts. By default, new
        accounts are assigned to account_user. Other possible values are
        account_publisher or the ID of one of the custom roles defined in
        the ArcGIS organization. To obtain the ID of a custom role,
         - Log in to the portal sharing directory.
         - Go to Portals > Self > Roles.
         - Copy the custom role ID you want to use.
        The allowedProxyHosts property restricts what hosts the portal can
        access directly. This restriction applies to several scenarios,
        including when the portal accesses resources from a server that
        does not support Cross Origin Resource Sharing (CORS) or when
        saving credentials used to access a secure service. By default,
        this property is not defined and no restrictions are applied.
        Define the allowedProxyHosts with a comma-separated list of
        hostnames to restrict the hosts the portal can access directly. Use
        the format (.*).domain.com to allow access to all machines within a
        specified domain.

        *example value*
          {
           "disableServicesDirectory":false,
           "enableAutomaticAccountCreation":true,
           "defaultRoleForUser": 12aBC3D4EF5ghIJ
          }
        """
        url = "%s/config/update" % self._url
        params = {
            "securityConfig" : value,
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def update_identity_store(self,
                              user_config=None,
                              group_config=None):
        """
        You can use this operation to change the identity provider and
        group store configuration in your portal. When Portal for ArcGIS is
        first installed, it supports token-based authentication and
        built-in groups using the built-in identity store for accounts. To
        configure your portal to connect to your enterprise authentication
        mechanism and group store, it must be configured to use an
        enterprise identity store such as Windows Active Directory or LDAP.

        See: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Update_Identity_Store/02r300000249000000/

        Parameters:
         :user_config: user store configuration
         :group_config: group store configuration
        """
        url = "%s/config/updateIdentityStore" % self._url
        if user_config is None:
            user_config = {
                "type": "BUILTIN",
                "properties": {"isPasswordEncrypted": "true"}
            }
        if group_config is None:
            group_config = {
                "type": "BUILTIN",
                "properties": {"isPasswordEncrypted": "true"}
            }
        params = {
            "userStoreConfig": user_config,
            "groupStoreConfig": group_config,
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    @property
    def test_identity_store(self,
                            user_config=None,
                            group_config=None):
        """
        This operation can be used to test the connection to a user or
        group store.

        Parameters:
         :user_config: user store configuration
         :group_config: group store configuration

        """
        if user_config is None and \
           group_config is None:
            return
        params = {
            "f" : "json"
        }
        url = "%s/config/testIdentityStore" % self._url
        if user_config is not None:
            user_config = {
                "type": "BUILTIN",
                "properties": {"isPasswordEncrypted": "true"}
            }
            params["userStoreConfig"] = user_config
        if group_config is not None:
            group_config = {
                "type": "BUILTIN",
                "properties": {"isPasswordEncrypted": "true"}
            }
            params["groupStoreConfig"] = group_config

        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    @property
    def ssl(self):
        """
        Provides access to managing and updating SSL Certificates on a
        Portal site.
        """
        if self._ssl is None:
            url = "%s/sslCertificates" % self._url
            self._ssl = SSLCertificates(url=url, gis=self._gis)
        return self._ssl
########################################################################
class OAuth(BasePortalAdmin):
    """
    The OAuth resource contains a set of operations that update the
    OAuth2-specific properties of registered applications in Portal for
    ArcGIS.
    """
    _gis = None
    _con = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis=None, **kwargs):
        """Constructor"""
        super(OAuth, self).__init__(url=url,
                                    gis=gis,
                                    **kwargs)
        initialize = kwargs.pop("initialize", False)
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self._init(self._gis)
    #----------------------------------------------------------------------
    def update(self, current_id, new_id):
        """
        When new applications are registered with Portal for ArcGIS, a new
        client ID is generated for the application. This allows the
        application to access content from the portal. The new client ID
        does not work if the application developer has programmed against a
        specific ID. This operation can, therefore, be used to change the
        client ID to another value as specified by the application
        developer.

        Parameters:
         :current_id:The current client ID of an existing application.
         :new_id: The new client ID to assign to the application.
        """
        params = {"f" : "json",
                  "currentAppID" : current_id,
                  "newAppID" : new_id}
        url = "%s/changeAppID" % self._url
        res = self._con.post(path=url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        elif 'success' in res:
            return res['success']
        return res
    #----------------------------------------------------------------------
    @property
    def app_info(self):
        """
        Every application registered with Portal for ArcGIS has a unique
        client ID and a list of redirect URIs that are used for OAuth. This
        operation returns these OAuth-specific properties of an
        application. You can use this information to update the redirect
        URIs by using the Update App Info operation.
        """
        url = "%s/getAppInfo" % self._url
        params = {"f" : "json"}
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    @app_info.setter
    def app_info(self, value):
        """
        This operation allows you to update the OAuth-specific properties
        associated with an application. Use the Get App Info operation to
        obtain the existing OAuth properties that can be edited.
        """
        url = "%s/getAppInfo" % self._url
        params = {"f" : "json",
                  "appInfo" : value}
        return self._con.post(path=url, postdata=params)
########################################################################
class SSLCertificates(BasePortalAdmin):
    """
    Manages the Portal's SSL Certificates
    """
    _gis = None
    _con = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis=None, **kwargs):
        """Constructor"""
        super(SSLCertificates, self).__init__(url=url,
                                              gis=gis,
                                              **kwargs)
        initialize = kwargs.pop("initialize", False)
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self._init(self._gis)
    #----------------------------------------------------------------------
    def _refresh(self):
        """reloads all the properties of a given service"""
        self._init()
    #----------------------------------------------------------------------
    def update(self, alias, protocols, cipher_suites):
        """
        Use this operation to configure the web server certificate, SSL
        protocols, and cipher suites used by the portal.

        Parameters:
         :alias:The name of the certificate. This is a required
          parameter. The certificate must be already present in the
          portal.
         :protocols: The SSL protocols the portal will use. Valid
          options are TLSv1, TLSv1.1, and TLSv1.2; values must be comma
          separated. By default, these options are all enabled.
         :cipher_suites: The cipher suites the portal will use. Valid
          options are:
           - TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256
           - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
           - TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
           - TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA
           - TLS_RSA_WITH_AES_128_GCM_SHA256
           - TLS_RSA_WITH_AES_128_CBC_SHA256
           - TLS_RSA_WITH_AES_128_CBC_SHA
           - TLS_RSA_WITH_3DES_EDE_CBC_SHA
         By default, all of the above options are enabled. Values must
         be comma separated.
        """
        url = "%s/update" % self._url
        params = {
            "f" : "json",
            "webServerCertificateAlias" : alias,
            "sslProtocols" : protocols,
            "cipherSuites" : cipher_suites
        }
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def generate(self,
                 alias,
                 common_name,
                 organization,
                 key_algorithm="RSA",
                 validity=90,
                 key_size=2048,
                 signature_algorithm="SHA256withRSA",
                 unit="",
                 city="",
                 state="",
                 country_code="",
                 alt_name=""):
        """
        Use this operation to create a self-signed certificate or as a
        starting point for getting a production-ready CA-signed
        certificate. The portal will generate a certificate for you and
        store it in its keystore.

        Parameters:
         :alias: The name of the certificate. This is a required
          parameter.
         :common_name: The common name used to identify the server for
          which the certificate is to be generated. This is a required
          parameter.
         :organization: The name of the organization. This is a
          required parameter.
         :key_algorithm: The algorithm used to generate the key pairs.
          The default is RSA.
         :validity: The expiration time for the certificate in days.
          The default is 90.
         :key_size: The size of the key. The default is 2048.
         :signature_algorithm: The algorithm used to sign the
          self-signed certificates. The default is derived from the
          key_algorithm parameter.
         :unit: The department within which this server resides.
         :city: name of the city
         :state: name of the state
         :country_code: two letter abbrevation of the country
         :alt_name:	The common name used to identify the server for
          which the certificate is to be generated. This is a required
          parameter.
        """
        import json
        params = {
            "alias":alias,
            'keyAlg':key_algorithm,
            'keySize': key_size,
            'sigAlg':signature_algorithm,
            'cn':common_name.upper(),
            'orgUnit' : unit,
            'org':organization,
            'city': city,
            'state': state,
            'country':country_code,
            'validity': validity,
            'san':alt_name
        }
        url = "%s/generateCertificate" % self._url
        try:
            res = self._con.post(path=url, postdata=params)
        except json.JSONDecodeError:
            # Need to capture this because method only returns HTML
            # Ignore decoding errors
            self._refresh()
            return True
        except:
            return False

    #----------------------------------------------------------------------
    def import_certificate(self, certificate, alias):
        """
        This operation imports a certificate authority's (CA) root and
        intermediate certificates into the keystore.
        To create a production quality CA-signed certificate, you need
        to add the CA certificates into the keystore that enables the
        SSL mechanism to trust the CA (and the certificates it has
        signed). While most of the popular CA certificates are already
        available in the keystore, you can use this operation if you
        have a custom CA or specific intermediate certificates.

        Parameters:
         :certificate: path to the file path
         :alias: name of the certificate
        """

        from six.moves.urllib.error import HTTPError


        params = {
            "alias" : alias,
            "f" : "json"
        }
        files = {
            'file' : certificate
        }
        url = "%s/importRootOrIntermediate" % self._url
        try:
            res = self._con.post(path=url,
                                 add_headers=[('Accept', "*/*"), ('Accept-Encoding', 'gzip, deflate'),
                                              ('User-Agent', 'geosaurus/1.0'), ('Connection', 'keep-alive')],
                                 postdata=params,
                                 files=files)
        except HTTPError as error:
            if error.code == '408' or error.code == 408:
                return True
            return False
        except:
            return True
        return True
    #----------------------------------------------------------------------
    def import_server_certificate(self,
                                  alias,
                                  password,
                                  certificate):
        """
        This operation imports an existing server certificate, stored
        in the PKCS #12 format, into the keystore. If the certificate
        is a CA signed certificate, you must first import the CA Root
        or Intermediate certificate using the Import Root or
        Intermediate Certificate operation.

        Parameters:
         :alias: name of the certificate
         :password: password for the certificate file
         :certificate: certificate file
        """
        params = {
            "f" : "json",
            "password" : password,
            "alias" : alias
        }
        files = {
            "file" : certificate
        }
        url = "%s/importExistingServerCertificate" % self._url
        try:
            return self._con.post(path=url,
                                  postdata=params,
                                  files=files)
        except:
            return True
        return True
    #----------------------------------------------------------------------
    def list(self):
        """
        list of certificates
        """
        certs = []
        self._refresh()
        for cert in self.properties.sslCertificates:
            url = "%s/%s" % (self._url, cert)
            certs.append(SSLCertificate(url=url, gis=self._gis))
            del cert
        return certs
    #----------------------------------------------------------------------
    def get(self, alias_name):
        """
        gets a single SSLCertificate object by the alias name

        Parameters:
        :param alias_name: common name of the certificate
        Output:
        returns a single SSLCertificate object if it exists, else
        it returns None
        """
        for cert in self.list():
            if cert.properties['Alias name'].lower() == alias_name.lower():
                return cert
            del cert
        return None
########################################################################
class SSLCertificate(BasePortalAdmin):
    """
    represents a single registered certificate
    """
    _gis = None
    _con = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis=None, **kwargs):
        """Constructor"""
        super(SSLCertificate, self).__init__(url=url,
                                             gis=gis,
                                             **kwargs)
        initialize = kwargs.pop("initialize", False)
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self._init(self._gis)
    #----------------------------------------------------------------------
    def generate_csr(self, signing_request):
        """
        This operation generates a certificate signing request (CSR) for a
        self-signed certificate. A CSR is required by a CA to create a
        digitally signed version of your certificate.
        """
        params = {
            "f" : "json",
            "certificateSigningRequest" : signing_request
        }
        url = "%s/generateCsr" % self._url
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def export(self, out_path=None):
        """
        This operation downloads an SSL certificate. The file returned by
        the server is an X.509 certificate. The downloaded certificate can
        be imported into a client that is making HTTP requests.

        Parameters:
         :out_path: folder save location
        """
        if out_path is None:
            import tempfile
            out_path = tempfile.gettempdir()
        url = "%s/export" % self._url
        return self._con.get(path=url,
                             params={"f" : "json"},
                             out_folder=out_path)
    #----------------------------------------------------------------------
    def delete(self):
        """
        This operation deletes an SSL certificate from the key store. Once
        a certificate is deleted, it cannot be retrieved or used to enable
        SSL.
        """
        import json
        params = {"f" : "json"}
        url = "%s/delete" % self._url
        try:
            self._con.post(path=url, postdata=params)
            return True
        except json.JSONDecodeError:
            return True
        except:
            return False
    #----------------------------------------------------------------------
    def import_signed_certificate(self, file_path):
        """
        imports a certificate authority (CA) signed SSL certificate into
        the key store.

        Parameters:
         :file_path: location of the certificate on disk
        """
        url = "%s/importSignedCertificate" % self._url
        params = {'f' : "json"}
        return self._con.post(path=url,
                              postdata=params,
                              files={"file" : file_path})
########################################################################
class EnterpriseGroups(BasePortalAdmin):
    """
    The groups resource is an umbrella for operations to manage
    enterprise groups within the portal. The resource returns the total
    number of groups in the system.
    """
    _gis = None
    _con = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis=None, **kwargs):
        """Constructor"""
        super(EnterpriseGroups, self).__init__(url=url,
                                               gis=gis,
                                               **kwargs)
        initialize = kwargs.pop("initialize", False)
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self._init(self._gis)
    #----------------------------------------------------------------------
    def search(self,
               query="",
               max_count=255):
        """
        This operation searches groups in the configured enterprise group
        store. You can narrow down the search using the filter parameter.

        Parameters:
         :query: optional parameter to narrow group search
         :max_count: max number of records to return
        """
        params = {
            "f" : "json",
            "filter" : query,
            "maxCount" : max_count
        }
        url = "%s/searchEnterpriseGroups" % self._url
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def refresh_groups(self, groups):
        """
        This operation iterates over every enterprise account configured in
        the portal and determines if the user account is a part of the
        input enterprise group. If there are any change in memberships, the
        database and the indexes are updated for each group.
        While portal automatically refreshes the memberships during a user
        login and during a periodic refresh configured through the Update
        Identity Store operation, this operation allows an administrator to
        force a refresh.

        Parameters:
         :groups: comma seperated list of group names to be refreshed
        """
        url = "%s/refreshMembership" % self._url
        params = {
            "f" : "json",
            "groups" : groups
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def get_group_users(self, name, query="", max_count=255):
        """
        This operation returns the users that are currently assigned to the
        enterprise group within the enterprise user/group store. You can
        use the filter parameter to narrow down the user search.

        Parameters:
         :name: name of the enterprise group
         :query: optional filter to narror down the search
         :max_count: maximum number of users
        """
        url = "%s/getUsersWithinEnterpriseGroup" % self._url
        params = {
            "f" : "json",
            "groupName" : name,
            "filter" : query,
            "maxCount" : max_count
        }
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def get_user_groups(self, username,
                        query="", max_count=255):
        """
        This operation lists the groups assigned to a user account in the
        configured enterprise group store.

        Parameters:
         :username: name of the user account
         :query: wildcard string used to filter the search
         :max_count: number of groups to return
        """
        url = "%s/getEnterpriseGroupsForUser" % self._url
        params = {
            "f" : "json",
            "username" : username,
            "filter" : query,
            "maxCount" : max_count
        }
        return self._con.get(path=url, params=params)
########################################################################
class EnterpriseUsers(BasePortalAdmin):
    """
    The users resource is an umbrella for operations to manage members
    within Portal for ArcGIS. The resource returns the total number of
    members in the system.
    """
    _gis = None
    _con = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis=None, **kwargs):
        """Constructor"""
        super(EnterpriseUsers, self).__init__(url=url,
                                              gis=gis,
                                              **kwargs)
        initialize = kwargs.pop("initialize", False)
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self._init(self._gis)
    #----------------------------------------------------------------------
    def create(self,
               username,
               password,
               first_name,
               last_name,
               email,
               role="org_user",
               level=2,
               provider="arcgis",
               idp_username=None,
               description=None):
        """
        This operation is used to pre-create built-in or enterprise
        accounts within the portal. The provider parameter is used to
        indicate the type of user account.

        Parameters:
         :username: name of the user account
         :password: password of the user account
         :first_name: first name for the account
         :last_name: last name for the account
         :email: email for the account
         :role: The role for the user account. The default value is
          org_user.
          Values: org_user | org_publisher | org_admin
         :level: account level to assign the user.
          Values: 1 or 2
         :provider: The provider for the account. The default value is
          arcgis. Values: arcgis | enterprise
         :idp_username: The name of the user as stored by the enterprise
          user store. This parameter is only required if the provider
          parameter is enterprise.
         :description: optional description string
        """
        url = "%s/createUser" % self._url
        params = {
            "f" : "json",
            "username" : username,
            "password" : password,
            "firstname" : first_name,
            "lastname" : last_name,
            "email" : email,
            "role" : role,
            "level" : level,
            "provider" : provider
        }
        if idp_username:
            params['idpUsername'] =  idp_username
        if description:
            params['description'] = description
        res = self._con.post(path=url, postdata=params)
        return res['status'] == 'success'
    #----------------------------------------------------------------------
    def get(self, username):
        """
        This operation returns the description, full name, and email
        address for a single user in the enterprise identity (user) store
        configured with the portal. The username parameter is used to
        specify the enterprise username. If the user does not exist, an
        error is returned.

        Parameters:
         :username: Username of the enterprise account. For Windows Active
          Directory users, this can be either domain\\username or just
          username. For LDAP users, the format is always username.
        """
        url = "%s/getEnterpriseUsers" % self._url
        params = {
            "f" : "json",
            "username" : username
        }
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def update(self, username, idp_username):
        """
        This operation allows an administrator to update the idp_username
        for an enterprise user in the portal. This is used when migrating
        from accounts used with web-tier authentication to SAML
        authentication.

        Parameters:
         :username: username of the enterprise account
         :idp_username: username used by the SAML identity provider
        """
        url = "%s/updateEnterpriseUser" % self._url
        params = {
            "f" : "json",
            "username" : username,
            "idpUsername" : idp_username
        }
        res = self._con.get(path=url, params=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def search(self, query="", max_count=255):
        """
        This operation searches users in the configured enterprise user
        store. You can narrow down the search using the filter parameter.

        Parameters:
         :query: search criteria
         :max_count: maximum number of records returned
        """
        url = "%s/searchEnterpriseUsers" % self._url
        params = {
            "f" : "json",
            "filter" : query,
            "maxCount" : max_count
        }
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def refresh_users(self, users):
        """
        This operation iterates over every enterprise group configured in
        the portal and determines if the input user accounts belong to any
        of the configured enterprise groups. If there is any change in
        membership, the database and the indexes are updated for each user
        account. While portal automatically refreshes the memberships
        during a user login and during a periodic refresh (configured
        through the Update Identity Store operation), this operation allows
        an administrator to force a refresh.

        Parameters:
         :users: comma seperated list of users.
        """
        params = {
            "f" : "json",
            "users" : users
        }
        url = "%s/refreshMembership" % self._url
        return self._con.post(path=url, postdata=params)
