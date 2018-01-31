#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import listOfStr2listOfFloats, listOfStr2listOfInts

class LammpsDataFile(object):
    """

    Class  supporting LAMMPS data file.

    :param filename: data file to read initially
    :type filename: str
    :param atom_style: supported: *atomic*, *charge*, *molecular* and *full*
    :type atom_style: str
    :return: Lammps data file object
    :rtype: .LammpsDataFile

    """

    BlockKeywords = ['Masses', 'Atoms', 'Velocities', 'Bonds', 'Angles', 'Dihedrals', 'Impropers', 'Coeffs']


    def __init__(self, filename=None, atom_style='full'):
        self.atom_style = atom_style
        #: *Header* section data -> :class:`.LammpsDataHeader`
        self.header = LammpsDataHeader()
        #: *Masses* section data -> :class:`.LammpsDataMasses`
        self.masses = LammpsDataMasses()
        #: *Coefficients* section data -> :class:`.LammpsDataCoeffs`
        self.coeffs = LammpsDataCoeffs()
        self.BlockKeywords = LammpsDataFile.BlockKeywords + self.coeffs.coeffsSections
        #: *Atoms* section data -> :class:`.LammpsDataAtoms`
        self.atoms  = LammpsDataAtoms(self.atom_style)
        #: *Velocities* section data -> :class:`.LammpsDataVelocities`
        self.velos = LammpsDataVelocities()
        #: *Bonds* section data -> :class:`.LammpsDataBonds`
        self.bonds = LammpsDataBonds()
        #: *Bonds* section data -> :class:`.LammpsDataBonds`
        self.bonds = LammpsDataBonds()
        #: *Angles* section data -> :class:`.LammpsDataAngles`
        self.angles = LammpsDataAngles()
        #: *Dihedrals* section data -> :class:`.LammpsDataDihedrals`
        self.dihedrals = LammpsDataDihedrals()
        #: *Impropers* section data -> :class:`.LammpsDataImpropers`
        self.impropers = LammpsDataImpropers()

        self.dataObjs = [self.header, self.masses, self.coeffs, self.atoms,  self.velos, self.bonds, self.angles, self.dihedrals, self.impropers]

        if filename:
            self.filename = filename
            self._parse_file()


    def _parse_file(self):
        section = 'Header'
        f = open(self.filename, 'r')

        # read (1st) comment
        line = f.readline().strip()
        self.header['description'] = line
        i='.'
        #print '*: '+line
        for line in f:
            line = line.strip()
            kw = line.split('#')[0].strip()
            if line == '':
                continue
            if kw in self.BlockKeywords:
                #print '\n*: switch block ' + section + ' -> ' + line
                section = line.split('#')[0].strip()
                continue
            if section == 'Header':
                self.header.parseLine(line)
            elif section == 'Masses':
                self.masses.parseLine(line)
            elif section in self.coeffs.coeffsSections:
                self.coeffs.parseLine(section, line)
            elif section == 'Atoms':
                self.atoms.parseLine(line)
            elif section == 'Velocities':
                self.velos.parseLine(line)
            elif section == 'Bonds':
                self.bonds.parseLine(line)
            elif section == 'Angles':
                self.angles.parseLine(line)
            elif section == 'Dihedrals':
                self.dihedrals.parseLine(line)
            elif section == 'Impropers':
                self.impropers.parseLine(line)
            else:
                pass
                #print i,
        #print '\n<oef>'


    # def __str__(self):
    #     out = str(self.header)
    #     out += str(self.masses)
    #     out += str(self.coeffs)
    #     out += str(self.atoms)
    #     out += str(self.velos)
    #     out += str(self.bonds)
    #     out += str(self.angles)
    #     out += str(self.dihedrals)
    #     out += str(self.impropers)
    #     return out

    def __str__(self):
        out=''
        for dataObj in self.dataObjs:
            if len(dataObj) > 0:
                out += str(dataObj)
        return out


    # def write(self, filename):
    #     """
    #     Write a LAMMPS data file.
    #
    #     :param filename: LAMMPS data file name
    #     """
    #     myf = open(filename, 'w')
    #     myf.write(str(self.header))
    #     myf.write( str(self.masses))
    #     myf.write(str(self.coeffs))
    #     myf.write(str(self.atoms))
    #     myf.write(str(self.velos))
    #     myf.write(str(self.bonds))
    #     myf.write(str(self.angles))
    #     myf.write(str(self.dihedrals))
    #     myf.write(str(self.impropers))
    #     myf.close()

    def write(self, filename):
        """
        Write a LAMMPS data file.

        :param filename: LAMMPS data file name
        """
        myf = open(filename, 'w')
        for dataObj in self.dataObjs:
            if len(dataObj) > 0:
                myf.write(str(dataObj))
        myf.close()

    def xyz_print(self,title=''):
        print len(self.atoms)
        print self.header['description']
        print self.atoms._xyz_str

    @property
    def Lx(self):
        """ Box length in *X* dim. """
        return self.header['xhi'] - self.header['xlo']

    @property
    def Ly(self):
        """ Box length in *Y* dim. """
        return self.header['yhi'] - self.header['ylo']

    @property
    def Lz(self):
        """ Box length in *Z* dim. """
        return self.header['zhi'] - self.header['zlo']

    @property
    def Vol(self):
        """ Box volume """
        return self.Lx * self.Ly * self.Lz

    def move(self, vector):
        self.header.move(vector)
        self.atoms.move(vector)

    def scaleCharges(self, factor):
        self.atoms.scaleCharges( factor )

    def origin2zero(self):
        vector = [ -1.0 * self.header['xlo'],
                   -1.0 * self.header['ylo'],
                   -1.0 * self.header['zlo']]
        self.move( vector )

    def checkHeader(self):
        print self.header['atoms'], len(self.atoms)
        print self.header['bonds'], len(self.bonds)
        print self.header['angles'], len(self.angles)
        print self.header['dihedrals'], len(self.dihedrals)
        print self.header['impropers'], len(self.impropers)


#------------------------------------------------------------------------------------------------



class LammpsDataAtoms(dict):
    """
    Class for parsing, storage & administration of the **Atoms** section in the LAMMPS data file.

    Each individual atom is stored in an object, like :class:`.LammpsDataAtomAtomic`, which type
    depends on the *atom_style*, and is derived from  :class:`.LammpsDataAtomTemplate`.

    :param atom_style: supported: *atomic*, *charge*, *molecular* and *full*
    :type atom_style: str
    """

    _registeredStyles = {}

    @classmethod
    def _register(cls, registerCls):
        """
        Decorator to register Entry type classes.

        :param registerCls: class to register
        :type registerCls: class
        :return: class to register
        :rtype: class
        """
        style_name = registerCls.atom_style
        cls._registeredStyles[style_name] = registerCls
        return registerCls

    def __init__(self, atom_style):
        #self._atoms = {}
        super(LammpsDataAtoms, self).__init__()
        self.atom_class = self._registeredStyles[atom_style]


    def parseLine(self, line):
        """
        Creates a new atom by parsing a string.

        :param line: data line of the  *Atoms* section
        :type line: str
        """
        id = line.split()[0]
        self[int(id)] = self.atom_class(line)

    def __str__(self):
        out = '\nAtoms\n\n'
        for atom in self.values():
            out += str(atom)
        return out

    @property
    def ids(self):
        """ Returns a list of all atom IDs. """
        return self.keys()

    @property
    def _xyz_str(self):
        out = ''
        for atom in self.values():
            out += atom._xyz_str
        return out

    @property
    def totalCharge(self):
        charge=0.0
        for atom in self.values():
            charge += atom['q']
        return charge

    def move(self, vector):
        for atom in self.values():
            atom.move( vector )

    def scaleCharges(self, factor):
        for atom in self.values():
            atom.scaleCharge(factor)



class LammpsDataAtomTemplate(object):
    """
    Storage class template for an atom.

    """

    atom_style = 'template'
    props_int = ['id', 'atom-type']
    props_float = ['x', 'y', 'z']
    line_format = '%d %d %.6f %.6f %.6f\n'

    def __init__(self, line=None):
        self.props_all = self.props_int + self.props_float
        self._props = {}
        for prop in self.props_int:
            self._props[prop] = 0
        for prop in self.props_float:
            self._props[prop] = 0.0
        if line:
            self.parseLine(line)

    def parseLine(self, line):
        words = line.strip().split()
        i = 0
        for prop in self.props_int:
            self._props[prop] = int(words[i])
            i += 1
        for prop in self.props_float:
            self._props[prop] = float(words[i])
            i += 1

    def _list(self):
        lout = []
        for prop in self.props_all:
            lout.append( self._props[prop] )
        return lout

    def __str__(self):
        return str(self.line_format % tuple(self._list()))

    def __setitem__(self, prop, value):
        self._props[prop] = value

    def __getitem__(self, prop):
        return self._props[prop]

    def __getattr__(self, name):
        if name in type(self).props_int + type(self).props_float:
            return self._props[name]
        raise AttributeError

    def __setattr__(self, key, value):
        if key in type(self).props_int + type(self).props_float:
            self._props[key] = value
        else:
            super(LammpsDataAtomTemplate, self).__setattr__(key, value)

    @property
    def _xyz_str(self):
        tmp = [ self['atom-type'], self['x'], self['y'], self['z'] ]
        return str('%d %.6f %.6f %.6f\n' % tuple(tmp))

    @property
    def xyz(self):
        return  [ self['x'], self['y'], self['z'] ]

    def move(self, vector):
        self['x'] = self['x'] + vector[0]
        self['y'] = self['y'] + vector[1]
        self['z'] = self['z'] + vector[2]

    def scaleCharge(self, factor):
        self['q'] = self['q'] * factor


@LammpsDataAtoms._register
class LammpsDataAtomAtomic(LammpsDataAtomTemplate):
    """
    Basis: :class:`LammpsDataAtomTemplate`

    Storage class for an atom of style *atomic*.

    Supported properties: *id*, *atom-type*, *x*, *y*, *z*

    """
    atom_style = 'atomic'
    props_int = ['id', 'atom-type']
    props_float = ['x', 'y', 'z']
    line_format = '%d %d %.16e %.16e %.16e\n'

@LammpsDataAtoms._register
class LammpsDataAtomCharge(LammpsDataAtomTemplate):
    atom_style = 'charge'
    props_int = ['id', 'atom-type']
    props_float = ['q', 'x', 'y', 'z']
    line_format = '%d %d %.16e %.16e %.16e %.16e\n'

@LammpsDataAtoms._register
class LammpsDataAtomMolecular(LammpsDataAtomTemplate):
    atom_style = 'molecular'
    props_int = ['id', 'molecule-id', 'atom-type']
    props_float = ['x', 'y', 'z']
    line_format = '%d %d %d %.16e %.16e %.16e\n'


@LammpsDataAtoms._register
class LammpsDataAtomFull(LammpsDataAtomTemplate):
    atom_style = 'full'
    props_int = ['id', 'molecule-id', 'atom-type']
    props_float = ['q', 'x', 'y', 'z']
    line_format = '%d %d %d %.16e %.16e %.16e %.16e\n'


#------------------------------------------------------------------------------------------------


class LammpsDataVelocities(dict):
    """
    Class for parsing, storage & administration of the **Velocities** section in the LAMMPS data file.
    """

    def parseLine(self, line):
        words = line.strip().split()
        self[int(words[0])] =  listOfStr2listOfFloats(words[1:4])

    def __str__(self):
        out = '\nVelocities\n\n'
        for aid, vv in self.items():
            out += str("{0:d} {1:.16f} {2:.16f} {3:.16f}\n".format( aid, vv[0], vv[1], vv[2] ))
        return out

#------------------------------------------------------------------------------------------------

class LammpsDataBonds(dict):

    natoms = 2     # number of atoms involved in
    name = 'Bonds' # name of the section

    def parseLine(self, line):
        words = line.strip().split()
        self[int(words[0])] =  listOfStr2listOfInts(words[1:self.natoms+2])

    def __str__(self):
        out = '\n' + self.name + '\n\n'
        for id, vv in self.items():
            out += str("{0:d} ".format( id ))
            out += ' '.join(map(str, vv)) + '\n'
        return out

class LammpsDataAngles(LammpsDataBonds):
    natoms = 3
    name = 'Angles'

class LammpsDataDihedrals(LammpsDataBonds):
    natoms = 4
    name = 'Dihedrals'

class LammpsDataImpropers(LammpsDataBonds):
    natoms = 4
    name = 'Impropers'

#------------------------------------------------------------------------------------------------

class LammpsDataCoeffs(object):
    """
    Class for storage & administration of **the Coefficients sections** in the LAMMPS data file.

    Each individual section is stored in a :class:`.LammpsDataCoeffsSection` object.

    """

    #: List of supported Coefficients section names
    #:
    #:.. note:: This is the only position where a section name needs to be declared!
    #:
    coeffsSections = ['Pair Coeffs', 'PairIJ Coeffs', 'Bond Coeffs', 'Angle Coeffs', 'Dihedral Coeffs', 'Improper Coeffs',
                      'BondBond Coeffs','BondAngle Coeffs','MiddleBondTorsion Coeffs', 'EndBondTorsion Coeffs',
                      'AngleTorsion Coeffs', 'AngleAngleTorsion Coeffs','BondBond13 Coeffs','AngleAngle Coeffs' ]

    def __init__(self):
        self._coeffsSections = {}
        for coeffsSection in self.coeffsSections:
            self._coeffsSections[coeffsSection] = LammpsDataCoeffsSection(coeffsSection)

    def parseLine(self, section, line):
        self._coeffsSections[section].parseLine(line)

    def __str__(self):
        out = ''
        for coeffsType in self.coeffsSections:
            section = self._coeffsSections[coeffsType]
            if len(section) > 0:
                out += str(section)
        return out

    def __len__(self):
        for coeffsType in self.coeffsSections:
            section = self._coeffsSections[coeffsType]
            if len(section) > 0:
                return 1
        return 0


class LammpsDataCoeffsSection(object):
    """
    Class for parsing, storage & administration of **a Coefficients section** in the LAMMPS data file.

    :param coeffsType: Coeffs section name (see :attr:`.LammpsDataCoeffs.coeffsSections` )
    :type coeffsType: str
    """

    def __init__(self, coeffsType):
        self.type = coeffsType
        # key = atom type ID
        # value = [coeff1, coeff2, ...]
        self._coeffs = {}

    def __setitem__(self, key, value):
        self._coeffs[key] = value

    def __getitem__(self, key):
        return self._coeffs[key]

    def __len__(self):
        return len(self._coeffs)

    def parseLine(self, line):
        words = line.strip().split()
        self._coeffs[int(words[0])] = words[1:]

    def __str__(self):
        out = str("\n{0:s}\n\n".format(self.type))
        for cid, coeffs in self._coeffs.items():
            out += str("{0:d}".format(cid))
            for coef in coeffs:
                out += str(" {0:s}".format(coef))
            out += '\n'
        return out


class LammpsDataMasses(dict):
    """
    Class for parsing, storage & administration of the **Masses** sections in the LAMMPS data file.

    """

    def __setitem__(self, key, value):
        super(LammpsDataMasses, self).__setitem__(key, float(value))

    def parseLine(self, line):
        words = line.strip().split()
        self[int(words[0])] = float(words[1])

    def __str__(self):
        out = '\nMasses\n\n'
        for aid, mass in self.items():
            out += str("{0:d} {1:.6f}\n".format(aid, mass))
        return out


class LammpsDataHeader(object):
    """
    Class for parsing, storage & administration of the **Header** sections in the LAMMPS data file.

    """

    _HeaderKeywords = {
        2: ['atoms', 'bonds', 'angles', 'dihedrals', 'impropers'],
        3: ['atom types', 'bond types', 'angle types', 'dihedral types', 'improper types'],
        4: ['xlo', 'ylo', 'zlo']
    }

    def __init__(self):
        # initially define prop
        self._prop = dict(
            description='LAMMPS Description',
            atoms=0,
            bonds=0,
            angles=0,
            dihedrals=0,
            impropers=0,
            atom_types=0,
            bond_types=0,
            angle_types=0,
            dihedral_types=0,
            improper_types=0,
            xlo=0.0,
            xhi=0.0,
            ylo=0.0,
            yhi=0.0,
            zlo=0.0,
            zhi=0.0
        )

    def __getitem__(self, index):
        return self._prop[index.replace(' ','_')]

    def __setitem__(self, key, value):
        key = key.replace(' ','_')
        if key in self._prop.keys():
            self._prop[key] = value
        else:
            raise KeyError

    def parseLine(self, line):
        words = line.strip().split()
        nwords = len(words)
        if nwords >= 2 and nwords <= 4:
            if words[1] in LammpsDataHeader._HeaderKeywords[2]:
                self[words[1]] = int(words[0])
            elif words[1]+' types' in LammpsDataHeader._HeaderKeywords[3]:
                key = words[1]+' types'
                self[key] = int(words[0])
            elif words[2] in LammpsDataHeader._HeaderKeywords[4]:
                dim = words[2][0]
                self[dim + 'lo'] = float(words[0])
                self[dim + 'hi'] = float(words[1])
            else:
                return False
            return True
        else:
            return False

    def __str__(self):
        out = self['description'] + '\n\n'
        for kw in self._HeaderKeywords[2]:
            out += str("{0:d} {1:s}\n".format( self[kw], kw ))
        out += '\n'
        for kw in self._HeaderKeywords[3]:
            if  self[kw] is not 0:
                out += str("{0:d} {1:s}\n".format( self[kw], kw ))
        out += '\n'
        out += str("{0:.16e} {1:.16e} xlo xhi\n".format( self['xlo'], self['xhi'] ))
        out += str("{0:.16e} {1:.16e} ylo yhi\n".format( self['ylo'], self['yhi'] ))
        out += str("{0:.16e} {1:.16e} zlo zhi\n\n".format( self['zlo'], self['zhi'] ))
        return out

    def __len__(self):
        return 1

    def move(self, vector):
        cc={0: ('xlo', 'xhi'),
            1: ('ylo', 'yhi'),
            2: ('zlo', 'zhi')}
        for id, vals in cc.items():
            for val in vals:
                self[val] += vector[id]
