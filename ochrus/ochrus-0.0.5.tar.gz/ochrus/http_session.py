"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

import requests
import json
from xml.etree import ElementTree
import ssl


class HttpRequestSession(requests.sessions.Session):
    """Perform HTTP requests.
    
    Using: http://docs.python-requests.org/en/master/
    
    HttpSession subclass 'requests' session and add:
        1. URL w/o SSL, w/o port
        2. Authentication
        3. HTTP Headers modification
    
    Preparation:
        Install 'requests' as followed:
        >>> pip install requests    
        For more information about 'requests' go to: 
        http://docs.python-requests.org/en/master/
        
    Args:
        username (str):  Username for HTTP authentication
        password (str):  Password for HTTP authentication
        ip       (str):  Host IP     
        ssl      (bool): True/False [default=True]           
        verify   (bool): True when use certificate for authentication [default=False]          
    
    Returns:
        HttpResults class
         
    """

    #=========================================================================
    def __init__(self, ip, port=None, ssl=True, username=None, password=None,   
                                                  headers=None, verify=False):
        super(HttpRequestSession, self).__init__()
        
        self.ip = ip
        self.port = port
        self._ssl = ssl

        self.username = username
        self.password = password
        
        self.headers = headers
        self.verify = verify
    
    #=========================================================================
    @property        
    def ssl(self):
        if type(self._ssl)==str:
            ssl = str(self._ssl).lower()
            if ssl=="false" or ssl=="no":
                return False
            elif  ssl=="true" or ssl=="yes":
                return True
            
        if type(self._ssl)==int:
            if int(self._ssl) == 0:
                return False
            elif int(self._ssl) == 1:
                return True    

    @ssl.setter
    def ssl(self, ssl):
        self._ssl = ssl
            
    #=========================================================================    
    def _get_auth(self):
        if(self.username==None 
           or self.password==None):
            self.auth=None
        else:
            self.auth = (self.username, self.password)
    
    #=========================================================================
    def _get_url(self, uri):
        if self.ssl:
            url ="https"
        else:
            url = "http"    
        
        if(self.port is None):
            url = '{}://{}/{}'.format(url, self.ip, uri)
        else:
            url = '{}://{}:{}/{}'.format(url, self.ip, self.port, uri)
        return url
        
    #=========================================================================
    def get_str_payload(self, payload):
        if type(payload) == str:
            return payload
        elif type(payload) == dict:
            return json.dumps(payload)
            
            
    #=========================================================================
    def call_request(self, method, uri, data=None, json=None, **kwargs):
        """internal method used to implement http method. 
        
        Args:
            method (str): 'get', 'post', 'option', 'head', 'put', 'patch','delete'
            uri: the URI path (without the 'http'/'https', port and IP)
            data: data to send in body, e.g.: dict or string
            json: Json data to send in body, equal to: json.dumps({"a":"a"})
        
        Returns:
            - It will try to read the 'response.content' if it success it 
            return a tuple structure the content in first parameter and the 
            whole response object as the second tuple parameter.
            
            - If it failed it will return the same structure just instead
            of 'response.content' it will put an error message in a Json
            tuple: (requests.Response object, requests.Response.content)
                            
        """
        response = self.request(method=method, 
                                url=self._get_url(uri), 
                                auth=self._get_auth(), 
                                data=data,
                                json=json,
                                **kwargs)           
            
        self.close()
        return response, self.get_response_content(response)

    #=========================================================================
    def get_response_content(self, response):
        """
        Validate that response has content.
        
        Args:
            response: 'requests' is returning this object
        
        Returns:
            The response content or a Json with error message
        """
        try:
            response_content = response.content
        except ValueError:#will return ValueError if 'No data object could be decoded'
            return {"error":"No data object could be decoded"}
        except Exception as e:
            return {"error": "Except has occurs while trying to generate data: {}"\
                    .format(e.message)}
        else:
            return response_content


#=============================================================================
#=========                   HttpSession                          ============
#=============================================================================
class Http(HttpRequestSession):
    """ 
    Implements any HTTP method
    Get, Option, Head, Post, Put, Patch, Delete
    """
    #=========================================================================
    def __init__(self,*args, **kwargs):
        super(Http, self).__init__(*args, **kwargs)
            
    #=========================================================================
    def get(self, uri, **kwargs):
        """Sends a GET request.
        
        Args:
            uri: the URI path (without the 'http'/'https', port and IP)
        Returns:
            requests.Response object
        """
    
        kwargs.setdefault('allow_redirects', True)
        return self.call_request('get', uri, **kwargs)
    
    #=========================================================================
    def options(self, uri, **kwargs):
        """Perform an Option request.

        Args:
            uri: the URI path (without the 'http'/'https', port and IP)
        Returns:
            requests.Response object    
        """
    
        kwargs.setdefault('allow_redirects', True)
        return self.call_request('options', uri, **kwargs)
    
    #=========================================================================
    def head(self, uri, **kwargs):
        """Perform a Head request.

        Args:
            uri: the URI path (without the 'http'/'https', port and IP)
        Returns:
            requests.Response object
        """
    
        kwargs.setdefault('allow_redirects', False)
        return self.call_request('head', uri, **kwargs)
    
    #=========================================================================
    def post(self, uri, data=None, json=None, **kwargs):
        """Perform a Post request.
 
        Args:
            uri (str): the URI path (without the 'http'/'https', port and IP)
            data: data to send in body, e.g.: dict or string
            json: Json data to send in body, equal to: json.dumps({"a":"a"})
            
        Returns:
            requests.Response object
        """
        
        return self.call_request('post', uri, data=data, json=json, **kwargs)
    
    #=========================================================================
    def put(self, uri, data=None, json=None,**kwargs):
        """Perform a Put request.
    
        Args:
            uri (str): the URI path (without the 'http'/'https', port and IP)
            data: data to send in body, e.g.: dict or string
            json: Json data to send in body, equal to: json.dumps({"a":"a"})
            
        Returns:
            requests.Response object
        """
    
        return self.call_request('put', uri, data=data, json=json, **kwargs)
    
    #=========================================================================
    def patch(self, uri, data=None, json=None, **kwargs):
        """Perform a Patch request.
    
        Args:
            uri (str): the URI path (without the 'http'/'https', port and IP)
            data: data to send in body, e.g.: dict or string
            json: Json data to send in body, equal to: json.dumps({"a":"a"})
            
        Returns:
            requests.Response object
        """
    
        return self.call_request('patch', uri,  data=data, json=json, **kwargs)
    
    #=========================================================================
    def delete(self, uri, **kwargs):
        """Perform a Delete request.
    
        Args:
            uri: the URI path (without the 'http'/'https', port and IP)
        Returns:
            requests.Response object
        """
    
        return self.call_request('delete', uri, **kwargs)
 

#=============================================================================
#=========                   RestSession                          ============
#=============================================================================
class Rest(Http):
    def __init__(self,*args, **kwargs):
        super(Rest, self).__init__(*args, **kwargs)
        self.headers = {'content-type': 'application/json', 
                        'accept': 'application/json',}

    #=========================================================================
    def get_response_content(self, response):
        """
        Overlap method, translate 'response' content to Json
        
        Args:
            response: 'requests' is returning this object
        
        Returns:
            Json
        """
        try:
            response_content = response.content
        except ValueError:#will return ValueError if 'No data object could be decoded'
            return {"error":"No Json object could be decoded"}
        except Exception as e:
            return {"error": "Except has occurs while trying to generate Json: {}"\
                    .format(e.message)}
        else:
            return response_content


#=============================================================================
#=========                   SoapSession                          ============
#=============================================================================
class Soap(HttpRequestSession):
    def __init__(self,uri=None, *args, **kwargs):
        super(Soap, self).__init__(*args, **kwargs)
        self.headers = {'content-type': 'text/xml', 
                        'accept': 'text/xml',}
        self.uri = uri    

    #=========================================================================
    def get_response_content(self, response):
        """ Overlap method, verify 'response' content is a valid XML response
        
        Args:
            response: 'requests' is returning this object
        
        Returns:
            ElementTree object
        """
        try:
            response_content = ElementTree.fromstring(response.content)
        except ValueError:
            return "No ElementTree could be decoded"
        except Exception as e:
            return "Exception has occurs while trying to generate XML data: {}"\
                   .format(e.message)
        else:
            return response_content
    
    #========================================================================= 
    def post(self, soap_action, element_tree, **kwargs):
        """ Perform a SOAP Post request.
        
        Args:
            soap_action:  the 'SOAPAction:' value to add to the HTTP header
            element_tree: xml.etree.ElementTree 
            kwargs:       according to 'requests' parameters
        """
        self.headers.update({'SOAPAction':'{}'.format(soap_action)})
        data = '{}'.format(ElementTree.tostring(element_tree, 'utf-8', 'xml'))
        return self.call_request('post', self.uri, data=data, **kwargs)       
            
    #=========================================================================
    def post_xml(self, soap_action, xml_file):
        """ Perform HTTP Post request of an XML file.
        
        Args:
            soap_action:  the 'SOAPAction:' value to add to the HTTP header
            xml_file:     full path to XML file
        
        Returns:
            Tuple: (requests full response, the XML content)
        """
        xml_ET = self.load_xml(xml_file)
        return self.post(soap_action, xml_ET)
    
    
    #========================================================================= 
    def load_xml(self, xml_file):
        """ load XML file.
        
        Args:
            xml_file:     full path to XML file
            
        Returns:
            Root of the ElementTree object
        """
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()
        return root        
 
        