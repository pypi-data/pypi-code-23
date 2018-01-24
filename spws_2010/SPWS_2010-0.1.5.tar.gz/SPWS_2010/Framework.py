import SPWS_2010.config

import requests
import xmltodict
from lxml import etree
from requests_ntlm import HttpNtlmAuth

class soap(object):
	def __init__(self, operation, schema = ''):
		self.schema = schema
		MAP = {
			'SOAP-ENV' : "http://schemas.xmlsoap.org/soap/envelope/",
			'ns0' : "http://schemas.xmlsoap.org/soap/envelope/",
			'ns1' : "http://schemas.microsoft.com/sharepoint/soap/{}".format(self.schema),
			'xsi' : "http://www.w3.org/2001/XMLSchema-instance"
		}
		ENV = "{%s}" % MAP['SOAP-ENV']
		
		self.envelope = etree.Element(ENV + "Envelope", nsmap=MAP)
		self.operation = etree.SubElement(etree.SubElement(self.envelope,'{http://schemas.xmlsoap.org/soap/envelope/}Body'), '{http://schemas.microsoft.com/sharepoint/soap/%s}' % (self.schema) + operation)
	
	def add_parameter(self, parameter, value=None):
		sub = etree.SubElement(self.operation, '{http://schemas.microsoft.com/sharepoint/soap/%s}' % (self.schema) + parameter)
		if value:
			sub.text = value
			
	def __repr__(self):
		return (b"""<?xml version="1.0" encoding="utf-8"?>""" + etree.tostring(self.envelope)).decode('utf-8')
		
	def __str__(self, pretty_print=False):
		return (b"""<?xml version="1.0" encoding="utf-8"?>""" + etree.tostring(self.envelope, pretty_print=True)).decode('utf-8')

class SharePoint:
	def __init__(self, params, ssl=True):
		self.site = params['Site URL']
		self.name = params['Site Name']
		self.SSL = ssl
		self.Session = requests.Session()
		self.Session.headers.update({'user-agent' : 'SPWS-2010/0.1'})
		if params["Authorize"] != None:
			self.Session.auth = HttpNtlmAuth(params["Authorize"]['User'],params["Authorize"]['Password'])

	def soapHeaders(self, schema):
		return {"Content-Type" : "text/xml; charset = utf-8", "SOAPAction" : "http://schemas.microsoft.com/sharepoint/soap/{}".format(schema)}
	
	def soapPayload(self,schema,name,methods,values):
		payload = soap(name, schema)
		for param in methods[name]:
			payload.add_parameter(param, values[param])
		return str(payload)
	
	def soapRequest(self,schema,service,name,payload, params):
		response = self.Session.post(
			url = "{}{}".format(self.site, service),
			headers = self.soapHeaders("{}{}".format(schema,name)),
			data = payload,
			verify = self.SSL
		)
		if response == 200:
			if params['returnValue']:
				return xmltodict.parse(response.text)
			else:
				return response
		else:
			return response
		
class UserGroup(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = "directory/"
		self.Service = "/_vti_bin/UserGroup.asmx"
		self.Methods = {
			"AddGroup" : ["groupName","ownerIdentifier","ownerType","defaultUserLoginName","description"],
			"AddGroupToRole" : ["roleName","groupName"],
			"AddRole" : ["roleName","description","permissionMask"],
			"AddRoleDef" : ["roleName","description","permissionMask"],
			"AddUserCollectionToGroup" : ["groupName","userInfoXml"],
			"AddUserCollectionToRole" : ["roleName","userInfoXml"],
			"AddUserToGroup" : ["groupName","userName","userLoginName","userEmail","userNotes"],
			"AddUserToRole" : ["roleName","userName","userLoginName","userEmail","userNotes"],
			"GetAllUserCollectionFromWeb" : [],
			"GetCurrentUserInfo" : [],
			"GetGroupCollection" : ['groupNamesXml'],
			"GetGroupCollectionFromRole" : ["roleName"],
			"GetGroupCollectionFromSite" : [],
			"GetGroupCollectionFromUser" : ["userLoginName"],
			"GetGroupCollectionFromWeb" : [],
			"GetGroupInfo" : ["groupName"],
			"GetRoleCollection" : ['groupNamesXml'],
			"GetRoleCollectionFromGroup" : ["groupName"],
			"GetRoleCollectionFromUser" : ["userLoginName"],
			"GetRoleCollectionFromWeb" : [],
			"GetRoleInfo" : ["roleName"],
			"GetRolesAndPermissionsForCurrentUser" : [],
			"GetRolesAndPermissionsForSite" : [],
			"GetUserCollection" : ["userLoginNamesXml"],
			"GetUserCollectionFromGroup" : ["groupName"],
			"GetUserCollectionFromRole" : ["roleName"],
			"GetUserCollectionFromSite" : [],
			"GetUserCollectionFromWeb" : [],
			"GetUserInfo" : ["userLoginName"],
			"GetUserLoginFromEmail" : ["emailXml"],
			"RemoveGroup" : ["groupName"],
			"RemoveGroupFromRole" : ["roleName","groupName"],
			"RemoveRole" : ["roleName"],
			"RemoveUserCollectionFromGroup" : ["groupName","userLoginNamesXml"],
			"RemoveUserCollectionFromRole" : ["roleName","userLoginNamesXml"],
			"RemoveUserCollectionFromSite" : ["userLoginNamesXml"],
			"RemoveUserFromGroup" : ["groupName","userLoginName"],
			"RemoveUserFromRole" : ["roleName","userLoginName"],
			"RemoveUserFromSite" : ["userLoginName"],		
			"RemoveUserFromWeb" : ["userLoginName"],
			"UpdateGroupInfo" : ["oldGroupName","groupName","ownerIdentifier","ownerType","description"],
			"UpdateRoleDefInfo" : ["oldRoleName","roleName","description","permissionMask"],
			"UpdateRoleInfo" : ["oldRoleName","roleName","description","permissionMask"],
			"UpdateUserInfo" : ["userLoginName","userName","userEmail","userNotes"]
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)

class Permissions(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = "directory/"
		self.Service = "/_vti_bin/Permissions.asmx"
		self.Methods = {
			"AddPermission" : ["objectName","objectType","permissionIdentifier","permissionType","permissionMask"],
			"AddPermissionCollection" : ["objectName","objectType","permissionsInfoXml"],
			"GetPermissionCollection" : ["objectName","objectType"],
			"RemovePermission" : ["objectName","objectType","permissionIdentifier","permissionType"],
			"RemovePermissionCollection" : ["objectName","objectType","memberIdsXml"],
			"UpdatePermission" : ["objectName","objectType","permissionIdentifier","permissionType","permissionMask"]
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)

class Lists(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/Lists.asmx"
		self.Methods = {
			"AddAttachment" : ['listName','listItemID','fileName','attachment'],
			"AddDiscussionBoardItem" : ['listName','message'],
			"AddList" : ['listName','description','templateID'],
			"AddListFromFeature" : ['listName','description','featureID','templateID'],
			"AddWikiPage" : ['strListName','listRelPageUrl','wikiContent'],
			"ApplyContentTypeToList" : ['webUrl','contentTypeId','listName'],
			"CheckInFile" : ['pageUrl','comment','CheckinType'],
			"CheckOutFile" : ['pageUrl','checkoutToLocal','lastModified'],
			"CreateContentType" : ['listName','displayName','parentType','fields','contentTypeProperties','addToView'],
			"DeleteAttachment" : ['listName','listItemID','url'],
			"DeleteContentType" : ['listName','contentTypeId'],
			"DeleteContentTypeXmlDocument" : ['listName','contentTypeId','documentUri'],
			"DeleteList" : ['listName'],
			"GetAttachmentCollection" : ['listName','listItemID'],
			"GetList" : ['listName'],
			"GetListAndView" : ['listName','viewName'],
			"GetListCollection" : [],
			"GetListContentType" : ['listName','contentTypeId'],
			"GetListContentTypes" : ['listName','contentTypeId'],
			"GetListContentTypesAndProperties" : ['listName','contentTypeId','propertyPrefix','includeWebProperties','includeWebPropertiesSpecified'],
			"GetListItemChanges" : ['listName','viewFields','since','contains'],
			"GetListItemChangesSinceToken" : ['listName','viewName','query','viewFields','rowLimit','queryOptions','changeToken','contains'],
			"GetListItemChangesWithKnowledge" : ['listName','viewName','query','viewFields','rowLimit','queryOptions','syncScope','knowledge','contains'],
			"GetListItems" : ['listName','viewName','query','viewFields','rowLimit','queryOptions','webID'],
			"GetVersionCollection" : ['strlistID','strlistItemID','strFieldName'],
			"UndoCheckOut" : ['pageUrl'],
			"UpdateContentType" : ['listName','contentTypeId','contentTypeProperties','newFields','updateFields','deleteFields','addToView'],
			"UpdateContentTypesXmlDocument" : ['listName','newDocument'],
			"UpdateContentTypeXmlDocument" : ['listName','contentTypeId','newDocument'],
			"UpdateList" : ['listName','listProperties','newFields','updateFields','deleteFields','listVersion'],
			"UpdateListItems" : ['listName','updates'],
			"UpdateListItemsWithKnowledge" : ['listName','updates','syncScope','knowledge']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Sites(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/Sites.asmx"
		self.Methods = {
			"CreateWeb" : ['url','title','description','templateName','language','languageSpecified','locale','localeSpecified',
				'collationLocale','collationLocaleSpecified','uniquePermissions','uniquePermissionsSpecified',
				'anonymous','anonymousSpecified','presence','presenceSpecified'],
			"DeleteWeb" : ['url'],
			"ExportSolution" : ['solutionFileName','title','description','fullReuseExportMode','includeWebContent'],
			"ExportWeb" : ['jobName','webUrl','dataPath','includeSubwebs','includeUserSecurity','overWrite','cabSize'],
			"ExportWorkflowTemplate" : ['solutionFileName','title','description','workflowTemplateName','destinationUrl'],
			"GetSite" : ['siteUrl'],
			"GetSiteTemplates" : ['LCID','TemplateList'],
			"GetUpdatedFormDigest" : [],
			"GetUpdatedFormDigestInformation" : ['url'],
			"ImportWeb" : ['jobName','webUrl','dataFiles','logPath','includeUserSecurity','overWrite']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Sites(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/Sites.asmx"
		self.Methods = {
			"CreateWeb" : ['url','title','description','templateName','language','languageSpecified','locale','localeSpecified',
				'collationLocale','collationLocaleSpecified','uniquePermissions','uniquePermissionsSpecified',
				'anonymous','anonymousSpecified','presence','presenceSpecified'],
			"DeleteWeb" : ['url'],
			"ExportSolution" : ['solutionFileName','title','description','fullReuseExportMode','includeWebContent'],
			"ExportWeb" : ['jobName','webUrl','dataPath','includeSubwebs','includeUserSecurity','overWrite','cabSize'],
			"ExportWorkflowTemplate" : ['solutionFileName','title','description','workflowTemplateName','destinationUrl'],
			"GetSite" : ['siteUrl'],
			"GetSiteTemplates" : ['LCID','TemplateList'],
			"GetUpdatedFormDigest" : [],
			"GetUpdatedFormDigestInformation" : ['url'],
			"ImportWeb" : ['jobName','webUrl','dataFiles','logPath','includeUserSecurity','overWrite']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)

class Versions(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/Versions.asmx"
		self.Methods = {
			"DeleteAllVersions" : ['fileName'],
			"DeleteVersion" : ['fileName','fileVersion'],
			"GetVersions" : ['fileName'],
			"RestoreVersion" : ['fileName','fileVersion']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Views(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/Views.asmx"
		self.Methods = {
			"AddView" : ['listName','viewName','viewFields','query','rowLimit','type','makeViewDefault'],
			"DeleteView" : ['listName','viewName'],
			"GetView" : ['listName','viewName'],
			"GetViewCollection" : ['listName'],
			"GetViewHtml" : ['listName','viewName'],
			"UpdateView" : ['listName','viewName','viewProperties','query','viewFields','aggregations','formats','rowLimit'],
			"UpdateViewHtml" : ['listName','viewName','viewProperties','toolbar','viewHeader','viewBody','viewfooter','viewEmpty','rowLimitExceeded','query','viewFields','aggregations','formats','rowLimit'],
			"UpdateViewHtml2" : ['listName','viewName','viewProperties','toolbar','viewHeader','viewBody','viewfooter','viewEmpty','rowLimitExceeded','query','viewFields','aggregations','formats','rowLimit','openApplicationExtension']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Webs(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/Webs.asmx"
		self.Methods = {
			"CreateContentType" : ['displayName','parentType','newFields','contentTypeProperties'],
			"CustomizeCss" : ['cssFile'],
			"DeleteContentType" : ['contentTypeId'],
			"GetActivatedFeatures" : [],
			"GetAllSubWebCollection" : [],
			"GetColumns" : [],
			"GetContentType" : ['contentTypeId'],
			"GetContentTypes" : [],
			"GetCustomizedPageStatus" : ['fileUrl'],
			"GetListTemplates" : [],
			"GetObjectIdFromUrl" : ['objectUrl'],
			"GetWeb" : ['webUrl'],
			"GetWebCollection" : [],
			"RemoveContentTypeXmlDocument" : ['contentTypeId','documentUri'],
			"RevertAllFileContentStreams" : [],
			"RevertCss" : ['cssFile'],
			"RevertFileContentStream" : ['fileUrl'],
			"UpdateColumns" : ['newFields','updateFields','deleteFields'],
			"UpdateContentType" : ['contentTypeId','contentTypeProperties','newFields','updateFields','deleteFields'],
			"UpdateContentTypeXmlDocument" : ['contentTypeId','newDocument'],
			"WebUrlFromPageUrl" : ['pageUrl']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class SiteData(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/SiteData.asmx"
		self.Methods = {
			"EnumerateFolder" : ['strFolderUrl','vUrls'],
			"GetAttachments" : ['strListName','strItemId','vAttachments'],
			"GetChanges" : ['objectType','contentDatabaseId','startChangeId','endChangeId','Timeout','moreChanges'],
			"GetChangesEx" : ['version','xmlInput'],
			"GetContent" : ['objectType','objectId','folderUrl','itemId','retrieveChildItems','securityOnly','lastItemIdOnPage'],
			"GetList" : ['strListName','sListMetadata','vProperties'],
			"GetListCollection" : ['vLists'],
			"GetListItems" : ['strListName','strQuery','strViewFields','uRowLimit'],
			"GetSite" : ['sSiteMetadata','vWebs','strUsers','strGroups','vGroups'],
			"GetSiteAndWeb" : ['strUrl','strSite','strWeb'],
			"GetSiteUrl" : ['Url','siteUrl','siteId'],
			"GetURLSegments" : ['strURL','strWebID','strBucketID','strListID','strItemID'],
			"GetWeb" : ['sWebMetadata','vWebs','vLists','vFPUrls','strRoles','vRolesUsers','vRolesGroups']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class People(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/People.asmx"
		self.Methods = {
			"IsClaimsMode" : [],
			"ResolvePrincipals" : ['principalKeys','principalType','addToUserInfoList'],
			"SearchPrincipals" : ['searchText','maxResults','principalType']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Meetings(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = "meetings/"
		self.Service = "/_vti_bin/Meetings.asmx"
		self.Methods = {
			"AddMeeting" : ['organizeEmail','uid','sequence','utcDateStamp','title','location','utcDateStart','utcDateEnd','nonGregorian'],
			"AddMeetingFromICal" : ['organizeEmail','icalText'],
			"CreateWorkspace" : ['title','templateName','lcid','timeZoneInformation'],
			"DeleteWorkspace" : [],
			"GetMeetingsInformation" : ['requestFlags','lcid'],
			"GetMeetingsWorkspaces" : ['recurring'],
			"RemoveMeeting" : ['recurrenceId','uid','sequence','utcDateStamp','cancelMeeting'],
			"RestoreMeeting" : ['uid'],
			"SetAttendeeResponse" : ['attendeeEmail','recurrenceId','uid','sequence','utcDateTimeOrganizerCriticalChange'
				'utcDateTimeAttendeeCriticalChange','response'],
			"SetWorkspaceTitle" : ['title'],
			"UpdateMeeting" : ['uid','sequence','utcDateStamp','title','location','utcDateStart','utcDateEnd','nonGregorian'],
			"UpdateMeetingFromICal" : ['icalText','ignoreAttendees']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Imaging(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = "ois/"
		self.Service = "/_vti_bin/Imaging.asmx"
		self.Methods = {
			"CheckSubwebAndList" : ['strUrl'],
			"CreateNewFolder" : ['strListName','strParentFolder'],
			"Delete" : ['strListName','strFolder','itemFileNames'],
			"Download" : ['strListName','strFolder','itemFileNames','type','fFetchOriginalIfNotAvailable'],
			"Edit" : ['strListName','strFolder','itemFileName','recipe'],
			"GetItemsByIds" : ['strListName','ids'],
			"GetItemsXmlData" : ['strListName','strFolder','itemFileNames'],
			"GetListItems" : ['strListName','strFolder'],
			"ListPictureLibrary" : [],
			"Rename" : ['strListName','strFolder','request'],
			"Upload" : ['strListName','strFolder','bytes','fileName','fOverWriteIfExist']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Forms(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/Forms.asmx"
		self.Methods = {
			"GetForm" : ['listName','formUrl'],
			"GetFormCollection" : ['listName']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class DocumentWorkspace(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = "dws/"
		self.Service = "/_vti_bin/DWS.asmx"
		self.Methods = {
			"CanCreateDwsUrl" : ['url'],
			"CreateDws" : ['name','users','title','documents'],
			"CreateFolder" : ['url'],
			"DeleteDws" : [],
			"DeleteFolder" : ['url'],
			"FindDwsDoc" : ['id'],
			"GetDwsData" : ['document','lastUpdate'],
			"GetDwsMetaData" : ['document','id','minimal'],
			"RemoveDwsUser" : ['id'],
			"RenameDws" : ['title'],
			"UpdateDwsData" : ['updates','meetingInstance']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Copy(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_bin/Copy.asmx"
		self.Methods = {
			"CopyIntoItems" : ['SourceUrl','DestinationUrls','Fields','Stream','Results'],
			"CopyIntoItemsLocal" : ['SourceUrl','DestinationUrls','Results'],
			"GetItem" : ['Url','Fields','Stream']
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Alerts(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = "2002/1/alerts/"
		self.Service = "/_vti_bin/Alerts.asmx"
		self.Methods = {
			"DeleteAlerts" : ['IDs'],
			"GetAlerts" : []
		}
		
	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)
		
class Admin(SharePoint):
	def __init__(self, params):
		SharePoint.__init__(self, params)
		self.Schema = ""
		self.Service = "/_vti_adm/Admin.asmx"
		self.Methods = {
			"CreateSite" : ['Url','Title','Description','Lcid','WebTemplate','OwnerLogin','OwnerName','OwnerEmail','PortalUrl','PortalName'],
			"DeleteSite" : ['Url'],
			"GetLanguages" : [],
			"RefreshConfigCache" : ['VirtualServerId','AdminGroupChanged']
		}

	def execute(self, operation, parameters):
		payload = self.soapPayload(self.Schema, operation, self.Methods, parameters)
		return self.soapRequest(self.Schema, self.Service, operation, payload, parameters)	