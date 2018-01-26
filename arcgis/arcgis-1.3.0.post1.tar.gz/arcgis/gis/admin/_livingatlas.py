"""
class to work with the living atlas
"""
from ..._impl.connection import _ArcGISConnection
from ..._impl.common._mixins import PropertyMap
from ...gis import GIS
from ...gis import Group, GroupManager
from ._base import BasePortalAdmin
########################################################################
class LivingAtlas(BasePortalAdmin):
    """
    Living Atlas of the World content is a collection of authoritative,
    ready-to-use, global geographic content available from ArcGIS Online.
    The content includes valuable maps, data layers, tools, services and
    apps for geographic analysis.
    When you make Living Atlas content available to your portal members,
    you're providing them with ready-made content that they can use
    alone or in combination with their own content to create maps,
    scenes, and apps and perform analysis in the portal map viewer or
    Insights for ArcGIS.

    :Note:
       Your portal must have access to the Internet to use Living Atlas
       content from ArcGIS Online

    Types of content available
    All the Living Atlas content you access from Portal for ArcGIS was
    created by Esri. If your portal can connect to the Internet, the
    following three levels of Living Atlas content are available to you from
    ArcGIS Online:
      1). Content that does not require you to sign in to an ArcGIS Online
          account
          - This content is available by default in Portal for ArcGIS.
      2). Subscriber content
          - Subscriber content is the collection of ready-to-use map layers,
            analytic tools, and services published by Esri that requires an
            ArcGIS Online organizational subscription account to access. This
            includes layers from Esri such as Landsat 8 imagery, NAIP imagery,
            landscape analysis layers, and historical maps. Subscriber content
            is provided as part of your organizational subscription and does
            not consume any credits. Layers included in the Living Atlas
            subscriber content are suitable for use with analysis tools.
      3). Premium content
         - Premium content is a type of subscriber content that requires an
         ArcGIS Online organizational subscription account to access and
         consumes credits. Access and credit information is listed in the
         description details for each item.
         Premium content provides portal members with access to ready-to-use
         content such as demographic and lifestyle maps as well as tools for
         geocoding, geoenrichment, network analysis, elevation analysis, and
         spatial analysis.


    ===============     ====================================================
    **Argument**        **Description**
    ---------------     ----------------------------------------------------
    url                 required string, the web address of the site to
                        manage licenses.
                        example:
                        https://<org url>/<wa>/portaladmin/system/content/livingatlas
    ---------------     ----------------------------------------------------
    gis                 required GIS, the gis connection object.
    ===============     ====================================================
    """
    _groupquery = None
    _con = None
    _url = None
    _json_dict = None
    _json = None
    _properties = None
    _living_atlas_group = None
    _living_atlas_content_group = None
    _groups = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis):
        """Constructor"""

        super(LivingAtlas, self).__init__(url=url, gis=gis)
        self._url = url.replace("http://", "https://")
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")

        self._init()
    #----------------------------------------------------------------------
    def _init(self, connection=None):
        """initializer"""
        try:
            self._groupquery = self._gis.properties['livingAtlasGroupQuery']
        except:
            self._groupquery = 'title:"Living Atlas" AND owner:esri_livingatlas'
        groups = self._gis.groups
        self._groups = []
        for group in groups.search(query=self._groupquery):
            if group.title.lower() == "living atlas".lower():
                self._living_atlas_group =  group
            elif group.title.lower() == 'Living Atlas Analysis Layers'.lower():
                self._living_atlas_content_group = group
            self._groups.append(group)
            del group
        del groups
        self._properties = PropertyMap({})
    #----------------------------------------------------------------------
    def enable_public_access(self):
        """
        Enables the Public Living Atlas content.

        Living Atlas of the World content is a collection of authoritative,
        ready-to-use, global geographic content available from ArcGIS Online.
        The content includes valuable maps, data layers, tools, services and
        apps for geographic analysis.

        :returns:
           boolean. True means enabled, False means failure to enable.

        """
        url = self._url + "/share"
        results = []
        for g in self.groups:
            params = {
                "f" : "json",
                "groupId" : g.id,
                "type" : "Public"
            }
            res = self._con.post(path=url, postdata=params)
            results.append(res['status'] == 'success')
        return all(results)
    #----------------------------------------------------------------------
    def disable_public_access(self):
        """
        Disables the Public Living Atlas content.

        :returns:
           boolean. True means enabled, False means failure to enable.

        """
        url = self._url + "/unshare"
        results = []
        for g in self.groups:
            params = {
                "f" : "json",
                "groupId" : g.id,
                "type" : "Public"
            }
            res = self._con.post(path=url, postdata=params)
            results.append(res['status'] == 'success')
        return all(results)
    #----------------------------------------------------------------------
    def status(self, group):
        """
        returns the information about the sharing status of the Living
        Atlas

        ===============     ====================================================
        **Argument**        **Description**
        ---------------     ----------------------------------------------------
        group               required string or Group object
        ===============     ====================================================
        """
        url = "%s/status" % self._url
        params = {"f" : "json"}
        if isinstance(group, str):
            params["groupId" ] = group
        elif isinstance(group, Group):
            params['groupId'] = group.id
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    @property
    def groups(self):
        """returns a list of all living atlas groups"""
        if self._groups is None:
            self._init()
        return self._groups
    #----------------------------------------------------------------------
    def validate_credentials(self, username, password, online_url=None):
        """
        returns the information about the sharing status of the Living
        Atlas

        ===============     ====================================================
        **Argument**        **Description**
        ---------------     ----------------------------------------------------
        username            required string, username for AGOL
        ---------------     ----------------------------------------------------
        password            required string, login password for AGOL account
        ---------------     ----------------------------------------------------
        online_url          optional string, Url to ArcGIS Online site.
                            default is https://www.arcgis.com
        ===============     ====================================================

        :returns:
          boolean
        """
        if online_url is None:
            online_url = "https://www.arcgis.com"
        url = "%s/validate" % self._url
        params = {
            "username" : username,
            "password" : password,
            "onlineUrl" : online_url,
            "f" : "json",
        }
        res = self._con.post(path=url, postdata=params)
        return res['status'] == 'success'
    #----------------------------------------------------------------------
    def enable_premium_atlas(self, username, password):
        """
        Enables the Premium Livinng Atlas Content for a local portal.

        Premium content is a type of subscriber content that requires an
        ArcGIS Online organizational subscription account to access and
        consumes credits. Access and credit information is listed in the
        description details for each item.
        Premium content provides portal members with access to ready-to-use
        content such as demographic and lifestyle maps as well as tools for
        geocoding, geoenrichment, network analysis, elevation analysis, and
        spatial analysis.

        ===============     ====================================================
        **Argument**        **Description**
        ---------------     ----------------------------------------------------
        username            required string, username for AGOL
        ---------------     ----------------------------------------------------
        password            required string, login password for AGOL account
        ===============     ====================================================

        :Note:
          This will cost you credits.


        """
        group_id = None
        for g in self.groups:
            if g.title.lower() == "living atlas":
                group_id = g.id
                break
        params = {
            "f" : "json",
            "username" : username,
            "password" : password,
            'type' : "Premium",
            'groupId' : group_id
        }
        url = "%s/enable" % self._url
        res = self._con.post(path=url, postdata=params)
        if 'status' in res and \
           res['status'] == 'success' and \
           group_id:
            url = "%s/share" % self._url
            params = {
                "f" : "json",
                "groupId" : group_id,
                "type" : 'Premium'
            }
            res = self._con.post(path=url, postdata=params)
            return res['status'] == 'success'
        else:
            return False
        return
    #----------------------------------------------------------------------
    def enable_subscriber_atlas(self, username, password):
        """
        Enables the Premium Livinng Atlas Content for a local portal.

        Subscriber content is the collection of ready-to-use map layers,
        analytic tools, and services published by Esri that requires an
        ArcGIS Online organizational subscription account to access. This
        includes layers from Esri such as Landsat 8 imagery, NAIP imagery,
        landscape analysis layers, and historical maps. Subscriber content
        is provided as part of your organizational subscription and does
        not consume any credits. Layers included in the Living Atlas
        subscriber content are suitable for use with analysis tools.


        ===============     ====================================================
        **Argument**        **Description**
        ---------------     ----------------------------------------------------
        username            required string, username for AGOL
        ---------------     ----------------------------------------------------
        password            required string, login password for AGOL account
        ===============     ====================================================

        :Note:
          This will **not** cost your organization credits.


        """
        group_ids = []
        for g in self.groups:
            group_ids.append(g.id)
        params = {
            "f" : "json",
            "username" : username,
            "password" : password,
            'type' : "Subscriber"
        }
        try:
            for ids in group_ids:
                params['groupId'] = ids
                url = "%s/enable" % self._url
                res = self._con.post(path=url, postdata=params)
            for ids in group_ids:
                url = "%s/share" % self._url
                params = {
                    "f" : "json",
                    "groupId" : ids,
                    "type" : 'Subscriber'
                }
                res = self._con.post(path=url, postdata=params)
            return True
        except:
            return False
    #----------------------------------------------------------------------
    def disable_subscriber_atlas(self):
        """
        Disables the Subscriber level Living Atlas Content for a local portal.

        """
        group_ids = []
        for g in self.groups:
            group_ids.append(g.id)
        params = {
            "f" : "json",
            'type' : "Subscriber"
        }
        try:
            for ids in group_ids:
                params['groupId'] = ids
                url = "%s/disable" % self._url
                res = self._con.post(path=url, postdata=params)
            for ids in group_ids:
                url = "%s/unshare" % self._url
                params = {
                    "f" : "json",
                    "groupId" : ids,
                    "type" : 'Subscriber'
                }
                res = self._con.post(path=url, postdata=params)
            return True
        except:
            return False
    #----------------------------------------------------------------------
    def disable_premium_atlas(self):
        """
        Disables the Premium Livinng Atlas Content for a local portal.

        """
        group_id = None
        for g in self.groups:
            if g.title.lower() == "living atlas":
                group_id = g.id
                break
        params = {
            "f" : "json",
            "groupId" : group_id,
            'type' : "Premium"
        }
        url = "%s/disable" % self._url
        res = self._con.post(path=url, postdata=params)
        if 'status' in res and \
           res['status'] == 'success' and \
           group_id:
            url = "%s/unshare" % self._url
            params = {
                "f" : "json",
                "groupId" : group_id,
                "type" : 'Premium'
            }
            res = self._con.post(path=url, postdata=params)
            return res['status'] == 'success'
        else:
            return False
        return False

