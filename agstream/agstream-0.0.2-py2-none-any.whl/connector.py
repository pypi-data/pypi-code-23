# -*- coding: utf-8 -*-
"""
    Created on 23 mai 2014
    
    @author: renaud
    
    
    Connector Module
    ----------------    
    
    This module contains necessary stuff to be connected to
    the Agriscope API.



"""

import json
import urllib

class AgspError(Exception):

    """ tp rùzepùrez;s!;cd4mlksdfmlsdfksmdflk
    
        Parameter
        ~~~~~~~~~
        
        Raw connecteur to the agriscope API
        -----------------------------------
        Class grouping necessary functions to talk with the agriscope server.
        It allows to be authentification and to get information on a specific account.
        
        Possibility to get the agribase's list
        
        Posibility to downloads data for each sensor
    
    """
    def __init__(self, value):
        self.value = value
    def __unicode__(self): 
        return repr(self.value)
    def __str__(self):
        return unicode(self).encode('utf-8')


class AgspConnecteur :
    """
    Raw connector to the Agriscope web service
    
    Handle the agriscope session id, store it and use it when calls to 
    agriscope api json web service
    """
    
    debug=True
    def __init__ (self, server = u'jsonapi.agriscope.fr' ):
        self.sessionOpen = False
        self.agspSessionId = 0
        self.server = u'http://' + server
        self.application = u'/agriscope-web/app'
        self.lastLogin = 'undefined'
        self.lastPassword = 'undefined'
        self.debug=False

    def set_debug(self, value):
        """
        Execution is verbose in debug mode
        
        :param value : True ou False
        """
        self.debug = value

    def login (self, login_p, password_p):
        """
        Allow to be authentificate in the agriscope server
        The authentification key (sessionId) received from the server is stored 
        in the AgspConneteur object
        :param login_p: User's login
        :param password_p : User's password
        
        :return: The authenfication status and the session id 
        """
        self.lastLogin = login_p
        self.lastPassword = password_p
        url = self.server + self.application + '?service=jsonRestWebservice&arguments={"jsonWsVersion":"1.0","method":"login","parameters":{"login":"' + login_p + '","password":"' + password_p + '"}}'
        obj = self.__executeJsonRequest (url,'login()')
        if obj['returnStatus'] != 'RETURN_STATUS_OK' :
            print("Failed to open the agriscope session for login " + login_p)
            print(obj['infoMessage'])
            self.sessionOpen = False
            self.agspSessionId = -1
        elif obj['loginOk'] == True:
            # print("Agriscope session open for login " + login_p)
            self.sessionOpen = True
            self.agspSessionId = obj['agriscopeSessionId']
        elif obj['loginOk'] == False:
            print("Agriscope session failed for login " + login_p)
            self.sessionOpen = False
            self.agspSessionId = obj['agriscopeSessionId']
        return (self.sessionOpen, self.agspSessionId)

    def getAgribases(self, sessionid_p = -1):
        """
        Return a raw dictionnary as received from the server
        By default the API is called with stored sessionId
        
        If a optionnal sessionId is specified, the function uses this one.
        
        :param: sessionid_p: Optionnal sessionId 
        
        :return: A raw dict as received from the server
        :rtype: dict
        """
        if sessionid_p == -1 :
            sessionid_p = self.agspSessionId
        
        url = self.server + self.application + '?service=jsonRestWebservice&arguments={"jsonWsVersion":"1.0","method":"getAgribases","parameters":{"agriscopeSessionId":' + unicode(sessionid_p) + '}}'
        return self.__executeJsonRequest(url, "getAgribases()") 
        
            
    def getSensorData(self, sensorId, from_p = None,  to_p = None):
        """
        Return timeseries as an array of data and date from the the sensor id.
        
        In 
        
        Use the period specified by the from_p and the to_p parameters.
        
        If from_p AND to_p is not specified, the period is choosen automatically from
        [now - 3 days => now]
        
        If from_p is not specified and to_p is specified, the function return a range 
        between [to_p - 3 days => to_p]
        
        
        :param: sensorId: Agriscope sensor id
        :param: from_p : Datetime 
        :param: to_p : Datetime 
         
        
        :return: A tuble of two array (datesArray[], valuesArray[])
        """
        id_p = self.agspSessionId
        from_p = long (from_p * 1000)
        to_p = long (to_p * 1000)

        url = self.server + self.application + '?service=jsonRestWebservice&arguments={"jsonWsVersion":"1.0","method":"getSensorData","parameters":{"personalKey":"DUMMY","sensorInternalId":'+unicode(sensorId)+',"agriscopeSessionId":' + unicode(id_p) + ',"from":' + unicode(from_p) + ',"to":' + unicode(to_p) + '}}'
        tmpJson= self.__executeJsonRequest(url, "getSensorData()") 
        return tmpJson['atomicResults'][0]['dataDates'],tmpJson['atomicResults'][0]['dataValues']
      
      
    def getAgribaseIntervaleInSeconds(self,serialNumber_p):
        """
        Return the sampling intervall for an Agribase
        
        :param: serialNumber_p: Agriscope serial number
         
        
        :return: A integer, samplin in second
        """
        url = "http://jsonmaint.agriscope.fr/tools/CHECK/agbs.php?sn=%d" % serialNumber_p
        json=self.__executeJsonRequest(url)
        returnv = -1
        if "intervalInSec" in json :
            tmp = json["intervalInSec"]
            if tmp == 'N/A' :
                return 15
            returnv = int(tmp)
        return returnv
    
    
    def __executeJsonRequest (self, url, method=""):
        try : 
            
            if self.debug == True :
                    print url
            str_response=""    
            # RECORD MODE
            retry=3
            i = 0
            while retry > 0 :
                try :
                    response = urllib.urlopen( url)
                    retry = -1
                except Exception, e:
                    retry = retry - 1
                    i = i+1
                    print str(i) + " retry connection "
                    
            if retry == 0 :
                print "Probleme de connexion pour aller vers " + url
                return
            str_response = response.read().decode('utf-8')

            if self.debug == True :
                print str_response
            obj = json.loads(str_response,strict=False)
            infomessage="N/A"
            if 'infoMessage' in obj :
                infomessage = obj['infoMessage']
                if  "session invalide" in infomessage:
                    if len(method) > 0 :
                        print u"Numero de session invalide dans l'appel de " + method +" par l'api."
                    else :
                        print u"Numero de session invalide  par l'api."
                        raise AgspError(u"Erreur de connection")
            return (obj)
        except Exception, e:
            print e.__doc__
            print e.message
            if len(method) > 0 :
                raise AgspError(u"Erreur de connection dans " + method )
            else :
                raise AgspError(u"Erreur de connection "  )
            
    debug = property(None, set_debug, None, "debug's docstring")
            
        
    """
    Return the two roots in the quadratic equation::

      a*x**2 + b*x + c = 0

    or written with math typesetting

    .. math:: ax^2 + bx + c = 0

    The returned roots are real or complex numbers,
    depending on the values of the arguments `a`, `b`,
    and `c`.

    Parameters
    ----------
    a: int, real, complex
       coefficient of the quadratic term
    b: int, real, complex
       coefficient of the linear term
    c: int, real, complex
       coefficient of the constant term
    verbose: bool, optional
       prints the quantity ``b**2 - 4*a*c`` and if the
       roots are real or complex

    Returns
    -------
    root1, root2: real, complex
        the roots of the quadratic polynomial.

    Raises
    ------
    ValueError:
        when `a` is zero

    See Also
    --------
    :class:`Quadratic`: which is a class for quadratic polynomials
        that also has a :func:`Quadratic.roots` method for computing
        the roots of a quadratic polynomial. There is also a class
        :class:`~linear.Linear` in the module :mod:`linear`
        (i.e., :class:`linear.Linear`).

    Notes
    -----
    The algorithm is a straightforward implementation of
    a very well known formula [1]_.

    References
    ----------
    .. [1] Any textbook on mathematics or
           `Wikipedia <http://en.wikipedia.org/wiki/Quadratic_equation>`_.

    Examples
    --------
    >>> roots(-1, 2, 10)
    (-5.3166247903553998, 1.3166247903553998)
    >>> roots(-1, 2, -10)
    ((-2-3j), (-2+3j))

    Alternatively, we can in a doc string list the arguments and
    return values in a table

    ==========   =============   ================================
    Parameter    Type            Description
    ==========   =============   ================================
    a            float/complex   coefficient for quadratic term
    b            float/complex   coefficient for linear term
    c            float/complex   coefficient for constant term
    r1, r2       float/complex   return: the two roots of
                                 the quadratic polynomial
    ==========   =============   ================================
    """
    