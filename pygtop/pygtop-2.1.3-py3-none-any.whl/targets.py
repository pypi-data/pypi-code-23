"""Contains target-specific objects and functions."""

from . import gtop
from . import pdb
from .interactions import Interaction, get_interaction_by_id
from .exceptions import NoSuchTargetError, NoSuchTargetFamilyError
from .shared import DatabaseLink, Gene, strip_html

def get_target_by_id(target_id):
    """Returns a Target object of the target with the given ID.

    :param int target_id: The GtoP ID of the Target desired.
    :rtype: :py:class:`Target`
    :raises: :class:`.NoSuchTargetError`: if no such target exists in the database"""

    if not isinstance(target_id, int):
        raise TypeError("target_id must be int, not '%s'" % str(target_id))
    json_data = gtop.get_json_from_gtop("targets/%i" % target_id)
    if json_data:
        return Target(json_data)
    else:
        raise NoSuchTargetError("There is no target with ID %i" % target_id)


def get_all_targets():
    """Returns a list of all targets in the Guide to PHARMACOLOGY database. This
    can take a few seconds.

    :returns: list of :py:class:`Target` objects"""

    json_data = gtop.get_json_from_gtop("targets")
    return [Target(t) for t in json_data]


def get_targets_by(criteria):
    """Get all targets which specify the criteria dictionary.

    :param dict criteria: A dictionary of `field=value` pairs. See the\
     `GtoP target web services page <http://www.guidetopharmacology.org/\
     webServices.jsp#targets>`_ for key/value pairs which can be supplied.
    :returns: list of :py:class:`Target` objects."""

    if not isinstance(criteria, dict):
        raise TypeError("criteria must be dict, not '%s'" % str(criteria))

    search_string = "&".join(["%s=%s" % (key, criteria[key]) for key in criteria])
    json_data = gtop.get_json_from_gtop("targets?%s" % search_string)
    if json_data:
        return [Target(t) for t in json_data]
    else:
        return []


def get_target_by_name(name):
    """Returns the target which matches the name given.

    :param str name: The name of the target to search for. Note that synonyms \
    will not be searched.
    :rtype: :py:class:`Target`
    :raises:  :class:`.NoSuchTargetError`: if no such target exists in the database."""

    if not isinstance(name, str):
        raise TypeError("name must be str, not '%s'" % str(name))
    targets = get_targets_by({"name": name})
    if targets:
        return targets[0]
    else:
        raise NoSuchTargetError("There is no target with name %s" % name)


def get_target_family_by_id(family_id):
    """Returns a TargetFamily object of the family with the given ID.

    :param int family_id: The GtoP ID of the TargetFamily desired.
    :rtype: :py:class:`TargetFamily`
    :raises: :class:`.NoSuchTargetFamilyError`: if no such family exists in the database"""

    if not isinstance(family_id, int):
        raise TypeError("family_id must be int, not '%s'" % str(family_id))
    json_data = gtop.get_json_from_gtop("targets/families/%i" % family_id)
    if json_data:
        return TargetFamily(json_data)
    else:
        raise NoSuchTargetFamilyError("There is no Target Family with ID %i" % family_id)


def get_all_target_families():
    """Returns a list of all target families in the Guide to PHARMACOLOGY database.

    :returns: list of :py:class:`TargetFamily` objects"""

    json_data = gtop.get_json_from_gtop("targets/families")
    return [TargetFamily(f) for f in json_data]



class Target:
    """A Guide to PHARMACOLOGY target object.

    :param json_data: A dictionary obtained from the web services."""

    def __init__(self, json_data):
        self.json_data = json_data
        self._target_id = json_data["targetId"]
        self._name = json_data["name"]
        self._abbreviation = json_data["abbreviation"]
        self._systematic_name = json_data["systematicName"]
        self._target_type = json_data["type"]
        self._family_ids = json_data["familyIds"]
        self._subunit_ids = json_data["subunitIds"]
        self._complex_ids = json_data["complexIds"]


    def __repr__(self):
        return "<Target %i (%s)>" % (self._target_id, self._name)


    def target_id(self):
        """Returns the target's GtoP ID.

        :rtype: int"""

        return self._target_id


    @strip_html
    def name(self):
        """Returns the target's name.

        :param bool strip_html: If ``True``, the name will have HTML entities stripped.
        :rtype: str"""

        return self._name


    @strip_html
    def abbreviation(self):
        """Returns the target's abbreviated name.

        :param bool strip_html: If ``True``, the abbreviation will have HTML entities stripped.
        :rtype: str"""

        return self._abbreviation


    @strip_html
    def systematic_name(self):
        """Returns the target's systematic name.

        :param bool strip_html: If ``True``, the name will have HTML entities stripped.
        :rtype: str"""

        return self._systematic_name


    def target_type(self):
        """Returns the target's type.

        :rtype: str"""

        return self._target_type


    def family_ids(self):
        """Returns the the family IDs of any families this target is a member of.

        :returns: list of ``int``"""

        return self._family_ids


    def families(self):
        """Returns a list of all target families of which this target is a member.

        :returns: list of :py:class:`TargetFamily` objects"""

        return [get_target_family_by_id(i) for i in self._family_ids]


    def subunit_ids(self):
        """Returns the the target IDs of all targets which are subunits of this
        target.

        :returns: list of ``int``"""

        return self._subunit_ids


    def subunits(self):
        """Returns a list of all targets which are subunits of this target.

        :returns: list of :py:class:`Target` objects"""

        return [get_target_by_id(id_) for id_ in self._subunit_ids]


    def complex_ids(self):
        """Returns the the target IDs of all targets of which this target is a
        subunit.

        :returns: list of ``int``"""

        return self._complex_ids


    def complexes(self):
        """Returns a list of all targets of which this target is a subunit.

        :returns: list of :py:class:`Target` objects"""

        return [get_target_by_id(id_) for id_ in self._complex_ids]


    @strip_html
    def synonyms(self):
        """Returns any synonyms for this target.

        :param bool strip_html: If ``True``, the synonyms will have HTML entities stripped.
        :returns: list of str"""

        return [synonym["name"] for synonym in self._get_synonym_json()]


    def database_links(self, species=None):
        """Returns any database links for this target.

        :param str species: If given, only links belonging to this species will be returned.
        :returns: list of  :class:`.DatabaseLink` objects."""

        if species:
            return [DatabaseLink(link_json) for link_json in self._get_database_json()
             if link_json["species"] and link_json["species"].lower() == species.lower()]
        else:
            return [DatabaseLink(link_json) for link_json in self._get_database_json()]


    def genes(self, species=None):
        """Returns any genes for this target.

        :param str species: If given, only genes belonging to this species will be returned.
        :returns: list of  :class:`.Gene` objects."""

        if species:
            return [Gene(gene_json) for gene_json in self._get_gene_json()
             if gene_json["species"] and gene_json["species"].lower() == species.lower()]
        else:
            return [Gene(gene_json) for gene_json in self._get_gene_json()]


    def interactions(self, species=None):
        """Returns any interactions for this target.

        :param str species: If given, only interactions belonging to this species will be returned.
        :returns: list of  :class:`.Interaction` objects."""

        if species:
            return [Interaction(interaction_json) for interaction_json in self._get_interactions_json()
             if interaction_json["targetSpecies"] and interaction_json["targetSpecies"].lower() == species.lower()]
        else:
            return [Interaction(interaction_json) for interaction_json in self._get_interactions_json()]



    get_interaction_by_id = get_interaction_by_id
    """Returns an Interaction object of a given ID belonging to the target.

    :param int interaction_id: The interactions's ID.
    :rtype: :py:class:`.Interaction`
    :raises: :class:`.NoSuchInteractionError`: if no such interaction exists in the database."""


    def ligands(self, species=None):
        """Returns any ligands that this target interacts with.

        :param str species: If given, only ligands belonging to this species will be returned.
        :returns: list of  :class:`.DatabaseLink` objects."""

        ligands = []
        for interaction in self.interactions(species=species):
            ligand = interaction.ligand()
            if ligand not in ligands:
                ligands.append(ligand)
        return ligands


    @pdb.ask_about_molecupy
    def gtop_pdbs(self, species=None):
        """Returns a list of PDBs which the Guide to PHARMACOLOGY says contain
        this target.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""
        if species is None:
            return [pdb["pdbCode"] for pdb in self._get_pdb_json() if pdb["pdbCode"]]
        else:
            return [pdb["pdbCode"] for pdb in self._get_pdb_json()
             if pdb["pdbCode"] and pdb["species"].lower() == species.lower()]


    @pdb.ask_about_molecupy
    def uniprot_pdbs(self, species=None):
        """Queries the RSCB PDB database with the targets's uniprot accessions.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :param str species: If given, only PDBs belonging to this species will be returned.
        :returns: list of ``str`` PDB codes"""

        uniprot_accessions = [
         link.accession() for link in self.database_links(species=species)
          if link.database() == "UniProtKB"
        ]
        if uniprot_accessions:
            results = pdb.query_rcsb_advanced("UpAccessionIdQuery", {
             "accessionIdList": ",".join(uniprot_accessions)
            })
            return [result.split(":")[0] for result in results] if results else []
        else:
            return []


    @pdb.ask_about_molecupy
    def all_pdbs(self, species=None):
        """Get a list of PDB codes using all means available - annotated and
        external.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :param str species: If given, only PDBs belonging to this species will be returned.
        :returns: list of ``str`` PDB codes"""

        return list(set(
         self.gtop_pdbs(species=species) +
         self.uniprot_pdbs(species=species)
        ))


    def _get_synonym_json(self):
        json_object = gtop.get_json_from_gtop(
         "targets/%i/synonyms" % self._target_id
        )
        return json_object if json_object else []


    def _get_database_json(self):
        json_object = gtop.get_json_from_gtop(
         "targets/%i/databaseLinks" % self._target_id
        )
        return json_object if json_object else []


    def _get_gene_json(self):
        json_object = gtop.get_json_from_gtop(
         "targets/%i/geneProteinInformation" % self._target_id
        )
        return json_object if json_object else []


    def _get_interactions_json(self):
        json_object = gtop.get_json_from_gtop(
         "targets/%i/interactions" % self._target_id
        )
        return json_object if json_object else []


    def _get_pdb_json(self):
        json_object = gtop.get_json_from_gtop(
         "targets/%i/pdbStructure" % self._target_id
        )
        return json_object if json_object else []



class TargetFamily:
    """A Guide to PHARMACOLOGY target family object.

    :param json_data: A dictionary obtained from the web services."""

    def __init__(self, json_data):
        self.json_data = json_data

        self._family_id = json_data["familyId"]
        self._name = json_data["name"]
        self._target_ids = json_data["targetIds"]
        self._parent_family_ids = json_data["parentFamilyIds"]
        self._sub_family_ids = json_data["subFamilyIds"]


    def __repr__(self):
        return "<'%s' TargetFamily>" % self._name


    def family_id(self):
        """Returns the family's GtoP ID.

        :rtype: int"""

        return self._family_id


    @strip_html
    def name(self):
        """Returns the family's name.

        :param bool strip_html: If ``True``, the name will have HTML entities stripped.
        :rtype: str"""

        return self._name


    def target_ids(self):
        """Returns the the target IDs of all targets in this family. Note that only
        immediate children are shown - if a family has subfamilies then it will
        not return any targets here - you must look in the sub-families.

        :returns: list of ``int``"""

        return self._target_ids


    def targets(self):
        """Returns a list of all targets in this family. Note that only
        immediate children are shown - if a family has subfamilies then it will
        not return any targets here - you must look in the sub-families.

        :returns: list of :py:class:`Target` objects"""

        return [get_target_by_id(i) for i in self._target_ids]


    def parent_family_ids(self):
        """Returns the the target IDs of all target families of which this
        family is a member.

        :returns: list of ``int``"""

        return self._parent_family_ids


    def parent_families(self):
        """Returns a list of all target families of which this family is a member.

        :returns: list of :py:class:`TargetFamily` objects"""

        return [get_target_family_by_id(i) for i in self._parent_family_ids]


    def sub_family_ids(self):
        """Returns the the target IDs of all arget families which are a member
        of this family.

        :returns: list of ``int``"""

        return self._sub_family_ids


    def sub_families(self):
        """Returns a list of all target families which are a member of this family.

        :returns: list of :py:class:`TargetFamily` objects"""

        return [get_target_family_by_id(i) for i in self._sub_family_ids]
