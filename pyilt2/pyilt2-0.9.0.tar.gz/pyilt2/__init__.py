# -*- coding: utf-8 -*-
"""
This package contains object classes and functions to access the Ionic Liquids Database - ILThermo (v2.0)
from NIST (Standard Reference Database #147) within Python.

Concept
-------

The :func:`pyilt2.query` function uses the *requests* module to carry out the query on the NIST server.
The resulting *JSON* object is then decoded to a Python dictionary (:doc:`resDict <resdict>`), which serves as input
to create a :class:`pyilt2.result` object.
The result object creates and stores for each hit of the query a :class:`pyilt2.reference` object,
which offers the method :meth:`pyilt2.reference.get` to acquire the full data (:doc:`setDict <setdict>`)
as a  :class:`pyilt2.dataset` object.

Classes & Functions
---------------------
"""

import requests
import numpy as np

__license__   = "MIT"
__docformat__ = 'reStructuredText'
__version__   = '0.9.0'

searchUrl = "http://ilthermo.boulder.nist.gov/ILT2/ilsearch"
dataUrl = "http://ilthermo.boulder.nist.gov/ILT2/ilset"

properties = {
    "a" :     ["xuYB", "Activity"],
    "phi" :   ["GVwU", "Osmotic coefficient"],
    "Xpeq" :  ["DzMB", "Composition at phase equilibrium"],
    "Xeut"  : ["yfBw", "Eutectic composition"],
    "Hc" :    ["lPRc", "Henry's Law constant"],
    "L" :     ["PaSR", "Ostwald coefficient"],
    "tline" : ["pQqW", "Tieline"],
    "Xucon" : ["flhF", "Upper consolute composition"],
    "Pc" :    ["LHzu", "Critical pressure"],
    "Tc" :    ["COYE", "Critical temperature"],
    "Pucon" : ["NlFx", "Upper consolute pressure"],
    "Tucon" : ["ZaiD", "Upper consolute temperature"],
    "Hap" :   ["EFWo", "Apparent enthalpy"],
    "capm" :  ["NhSc", "Apparent molar heat capacity"],
    "Hdil" :  ["anJL", "Enthalpy of dilution"],
    "Hmix" :  ["PVPy", "Enthalpy of mixing of a binary solvent with component"],
    "Hex" :   ["ZLMT", "Excess enthalpy"],
    "Hpm" :   ["pzmx", "Partial molar enthalpy "],
    "H" :     ["PKJE", "Enthalpy"],
    "HvT" :   ["lVZh", "Enthalpy function {H(T)-H(0)}/T"],
    "S" :     ["sOwZ", "Entropy"],
    "cp" :    ["bvSs", "Heat capacity at constant pressure"],
    "cv" :    ["WBwL", "Heat capacity at constant volume"],
    "cpe" :   ["ZCkr", "Heat capacity at vapor saturation pressure"],
    "Hfus" :  ["TnZY", "Enthalpy of transition or fusion"],
    "Hvap" :  ["mxiH", "Enthalpy of vaporization or sublimation"],
    "Peq" :   ["LAEF", "Equilibrium pressure"],
    "Teq" :   ["SCih", "Equilibrium temperature"],
    "Teut" :  ["gpGA", "Eutectic temperature"],
    "Tmot" :  ["qQWF", "Monotectic temperature"],
    "Tm" :    ["lcRG", "Normal melting temperature"],
    "s" :     ["pFXp", "Interfacial tension"],
    "n" :     ["MVEw", "Refractive index"],
    "rperm" : ["annu", "Relative permittivity"],
    "sos" :   ["IkPD", "Speed of sound"],
    "slg" :   ["TeIR", "Surface tension liquid-gas"],
    "econd" : ["bqdZ", "Electrical conductivity"],
    "Dself" : ["OphJ", "Self-diffusion coefficient"],
    "Tcond" : ["VvTh", "Thermal conductivity"],
    "Dterm" : ["THpm", "Thermal diffusivity"],
    "Dtrac" : ["KCfd", "Tracer diffusion coefficient"],
    "visc" :  ["blXM", "Viscosity"],
    "Tb" :    ["ctDv", "Normal boiling temperature"],
    "kS" :    ["IWte", "Adiabatic compressibility"],
    "Vapm" :  ["Jual", "Apparent molar volume"],
    "dens" :  ["Ehib", "Density"],
    "Vex" :   ["NTYG", "Excess volume"],
    "aV" :    ["iCPYM", "Isobaric coefficient of volume expansion"],
    "kT" :    ["Yxkd", "Isothermal compressibility"],
    "Vpm" :   ["jpiS", "Partial molar volume"]
}

def query(comp='', numOfComp=0, year='', author='', keywords='', prop=''):
    """ Starts a query on the Ionic Liquids Database from NIST.

    Each web form field is represented by a keyword argument.
    To specify the physical property you have to use the respective :doc:`abbreviation <props>`.
    The function returns a :class:`pyilt2.result` object, whether or not the query makes a hit.

    :param comp: Chemical formula (case-sensitive), CAS registry number, or name (part or full)
    :type comp: str
    :param numOfComp: Number of mixture components. Default '0' means *any* number.
    :type numOfComp: int
    :param year: Publication year
    :type year: int
    :param author: Author's last name
    :type author: str
    :param keywords: Keyword(s)
    :type keywords: str
    :param prop: Physical property by abbreviation. Default '' means *unspecified*.
    :return: result object
    :rtype: :class:`pyilt2.result`
    :raises pyilt2.propertyError: if the abbreviation for physical property is invalid
    """
    if prop:
        if prop not in properties.keys():
            raise propertyError(prop)
        else:
            prp = properties[prop][0]
    else:
        prp = ''
    params = dict(
        cmp = comp,
        ncmp = numOfComp,
        year = year,
        auth = author,
        keyw = keywords,
        prp = prp
    )
    r = requests.get(searchUrl, params=params)
    return result(r.json())


class result(object):
    """ Class to store query results.

    The :class:`.result` object is created by the :func:`pyilt2.query` function.
    Each hit of the query is represented by a :class:`pyilt2.reference` object.
    The build-in function :func:`len` returns the number of hits, respectively
    references stored in the result object.
    It is iterable, so you can simply iterate over references, like:

    .. code-block:: py

        # iterate over references
        for reference in result:
            ...

        # One can also access the individual references as items:
        first_reference = result[0]
        last_reference = result[-1]

    :param resDict: decoded JSON object
    :type resDict: dict
    """

    def __init__(self, resDict):

        #: original JSON object from NIST server decoded to a Python dictionary (:doc:`example <resdict>`)
        self.resDict = resDict

        self.refs = []
        for ref in self.resDict['res']:
            ref = self._makeRefDict( ref )
            self.refs.append( reference(ref) )
        self._currentRefIndex = 0

    def __len__(self):
        return len(self.refs)

    def __iter__(self):
        return self

    def next(self):
        if self._currentRefIndex < len(self):
            out = self.refs[self._currentRefIndex]
            self._currentRefIndex += 1
            return out
        self._currentRefIndex = 0
        raise StopIteration()

    def __getitem__(self, item):
        return self.refs[item]

    def _makeRefDict(self, refList):
        out = {}
        for i in range(0, len(refList)):
            out[ self.resDict['header'][i] ] = refList[i]
        return out


class reference(object):
    """ Class to store a reference.

    The :class:`.reference` objects will be created while initiating :class:`pyilt2.result` object.
    It contains just a few meta data. To acquire the full data set, it offers the :meth:`pyilt2.reference.get` method.

    :param refDict: part of ``resDict``
    :type refDict: dict
    """

    def __init__(self, refDict):
        self.refDict = refDict

    def __str__(self):
        return self.refDict['ref']

    @property
    def setid(self):
        """NIST setid (hash) as used as input for :class:`pyilt2.dataset`"""
        return self.refDict['setid']

    @property
    def prop(self):
        """Physical property"""
        return self.refDict['prp']

    @property
    def np(self):
        """Number of data points"""
        return int(self.refDict['np'])

    def get(self):
        """ Returns the full data according to this reference.

        :return: Dataset object
        :rtype: :class:`pyilt2.dataset`
        """
        return dataset(self.refDict['setid'])


class dataset(object):
    """ Class to request & store the full data set.

    The :class:`.dataset` object is created by the :meth:`pyilt2.reference.get` method.

    :param setid: NIST setid (hash)
    :type setid: str
    :raises pyilt2.setIdError: if setid is invalid
    """

    def __init__(self, setid):

        #: NIST setid (hash) of this data set
        self.setid = setid

        #: original JSON object from NIST server decoded to a Python dictionary (:doc:`example <setdict>`)
        self.setDict = {}

        #: :class:`numpy.ndarray` containing the data points
        self.data = np.array([])

        #: List containing the **description** for each column of the data set
        self.headerList = []

        #: List containing the **physical property** for each column of the data set
        self.physProps = []

        #: List containing the **physical units** for each column of the data set
        self.physUnits = []

        #: List containing the phase information (if it make sense) for each column of the data set
        self.phases = []

        self._initBySetid()
        self._dataHeader()
        self._dataNpArray()

    def __str__(self):
        return self.setDict['ref']['full']

    def _initBySetid(self):
        r = requests.get(dataUrl, params=dict(set=self.setid))
        # raise HTTPError
        r.raise_for_status()
        # check if response is empty
        if r.text == '':
            raise setIdError(self.setid)
        self.setDict = r.json()

    def _dataHeader(self):
        headerList = self.setDict['dhead']
        for col in headerList:
            prop = col[0].replace('<SUP>', '').replace('</SUP>', '')
            phase = col[1]
            if ',' in prop:
                tmp = prop.split(',')
                prop = tmp[0]
                units = tmp[1].strip()
            else:
                units = None
            prop = prop.replace(' ', '_')
            desc = prop
            if phase:
                desc = '{0:s}[{1:s}]'.format(prop, phase)
            if units:
                desc = '{0:s}/{1:s}'.format(desc, units)
            self.headerList.append(desc)
            self.physProps.append(prop)
            self.physUnits.append(units)
            self.phases.append(phase)
        self.headerLine = '  '.join(self.headerList)

    def _dataNpArray(self):
        raw = self.setDict['data']
        rows = len(raw)
        acols = 0
        for c in raw[0]:
            acols += len(c)
        self.data = np.zeros((rows, acols))
        for i in range(0, len(raw)):
            newrow = [item for sublist in raw[i] for item in sublist]
            for j in range(0, len(newrow)):
                self.data[i][j] = newrow[j]

    @property
    def shape(self):
        """Tuple of :py:attr:`.data` array dimensions."""
        return self.data.shape

    @property
    def listOfComponents(self):
        """List of component names as strings."""
        out = []
        for comp in self.setDict['components']:
            out.append( comp['name'] )
        return out

    @property
    def numberOfComponents(self):
        """Number of components as integer."""
        return len(self.setDict['components'])


class propertyError(Exception):
    """Exception if an invalid abbreviation (for physical property) is defined."""

    def __init__(self,prop):
        self.msg = 'Invalid abbreviation "{0:s}" for physical property!'.format(prop)

    def __str__(self):
        return repr(self.msg)


class setIdError(Exception):
    """Exception if the set NIST setid (hash) is invalid.

    Because the NIST web server still returns a HTTP status code 200,
    even if the set id is invalid (I would expect here a 404er!),
    this exception class was introduced.
    """
    def __init__(self,setid):
        self.msg = 'SetID "{0:s}" is unknown for NIST!'.format(setid)

    def __str__(self):
        return repr(self.msg)

