"""Objects not specific to ligands or targets."""

import re
import html

class DatabaseLink:
    """A link to an external database, containing accession and species
    information.

    :param json_data: A dictionary obtained from the web services."""

    def __init__(self, json_data):
        self.json_data = json_data

        self._accession = json_data["accession"]
        self._database = json_data["database"]
        self._url = json_data["url"]
        self._species = None if json_data["species"] == "None" else json_data["species"]


    def __repr__(self):
        return "<%s link (%s)%s>" % (
         self._database,
         self._accession,
         " for " + self._species if self._species else ""
        )


    def accession(self):
        """The Accession code."""

        return self._accession


    def database(self):
        """The Database being linked to."""

        return self._database


    def url(self):
        """The URL for this database entry."""

        return self._url


    def species(self):
        """The specific species the database entry refers to."""

        return self._species



class Gene:
    """A gene for a pyGtoP target.

    :param json_data: A dictionary obtained from the web services."""

    def __init__(self, json_data):
        self.json_data = json_data

        self._target_id = json_data["targetId"]
        self._species = json_data["species"]
        self._gene_symbol = json_data["geneSymbol"]
        self._gene_name = json_data["geneName"]
        self._official_gene_id = json_data["officialGeneId"]
        self._genomic_location = json_data["genomicLocation"]
        self._amino_acids = int(json_data["aminoAcids"]) if json_data["aminoAcids"] else 0
        self._transmembrane_domains = int(json_data["transmembraneDomains"]) if json_data["transmembraneDomains"] else 0
        self._pore_loops = int(json_data["poreLoops"]) if json_data["poreLoops"] else 0


    def __repr__(self):
        return "<%s Gene (%s)>" % (self._species, self._gene_symbol)


    def target_id(self):
        """The ID of the pyGtoP target derived from this gene."""

        return self._target_id


    def species(self):
        """The species the gene is from."""

        return self._species


    def gene_symbol(self):
        """The gene's code."""

        return self._gene_symbol


    def gene_name(self):
        """The gene's name."""

        return self._gene_name


    def official_gene_id(self):
        """The gene's official ID."""

        return self._official_gene_id


    def genomic_location(self):
        """The gene's location in its genome."""

        return self._genomic_location


    def amino_acids(self):
        """The number of amino acids the gene codes for."""

        return self._amino_acids


    def transmembrane_domains(self):
        """The number of amino acids in the resultant protein."""

        return self._transmembrane_domains


    def pore_loops(self):
        """The number of pore loops in the resultant protein."""

        return self._pore_loops



def strip_html(func):
    """A decorator which, when applied to a function, will add a 'strip_html'
    keyword argument - if set to True this will strip any HTML from the
    function's output."""

    cleaner = re.compile("<.*?>")
    def new_func(*args, strip_html=False, **kwargs):
        name = func(*args, **kwargs)
        if strip_html:
            if isinstance(name, str):
                return html.unescape(re.sub(cleaner, "", name))
            elif isinstance(name, list) or isinstance(name, tuple):
                return type(name)([html.unescape(re.sub(cleaner, "", n)) for n in name])
        else:
            return name
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    return new_func
