import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import json
import base64

class HTTPRequest():
    """
    This class helps to send request from client side to API, hosted on SimpleIntelligence.com.
    There are two functions in the class:
    sendImgRequest - converts image to base64 encoded string and sends request.
    sendStrRequest - encode string to base64 format and sends request.
    """

    def __init__(self, userAPIKey, DLtitle, data):
        """
        Constructs URL for HTTP request and initialize data. 

        Parameters
        ----------
        userAPIKey: str
            Received from simpleintelligence.com
        DLtitle: str
            Received from simpleintelligence.com
        data: str
            Path to your file or input string depend on used API 
        """
        self.data = data
        self.baseSimpleIntelURL = "https://simpleintelligence.com/ServingWebService/rest/apis/model/"
        self.fullSimpleIntelURL = self.baseSimpleIntelURL + DLtitle + "/" + userAPIKey;


    def sendRequest(self, inputString):
        """
        Sends HTTP request with URL, created by constructor.

        Parameters
        ----------
        inputString: str
            Parsed input data.

        Returns
        -------
        str
            Response from a server after HTTP request. 
        """
        headers = {'content-type': 'application/json'}
        r = requests.post(url=self.fullSimpleIntelURL,
                          headers=headers,
                          data=inputString,
                          verify=False)
        return r

    def sendImgRequest(self):
        """
        This function converts image to base64 encoded string.
        Creates appropriate JSON format and sends HTTP request.

        Returns
        -------
        str
            Response from a server after HTTP request. 
        """
        # Read and encode image file
        image = open(self.data, 'rb')
        image_read = image.read()
        # '.decode('utf-8')' is needed for python 2 and 3 compitability: 
        # encodestring in python2 returns <str>; in python3 returns <bytes>
        imageString = base64.encodestring(image_read).decode('UTF-8')
        # Create JSON format
        jsonImageString={"inputAsStrings": [imageString]}
        inputString = json.dumps(jsonImageString)
        return self.sendRequest(inputString)

    def sendStrRequest(self):
        """
        Encodes input string to base64 format and sends HTTP request as JSON.
         
        Returns
        -------
        str
            Response from a server after HTTP request. 
        """

        # .encode('UTF-8') is needed for python 2 and 3 compitability:
        # for .encodestring in python2 argument is <str>; in python3 argument is <bytes>
        # '.decode('utf-8')' is needed for python 2 and 3 compitability: 
        # .encodestring in python2 returns <str>; in python3 returns <bytes>

        strToBytes = self.data.encode('UTF-8')
        strTo64 = base64.encodestring(strToBytes).decode('UTF-8')
        jsonString = {"inputAsStrings": [strTo64]}
        inputString = json.dumps(jsonString)
        return self.sendRequest(inputString)


