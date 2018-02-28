import a99
from f311.filetypes import DataFile
from astropy.io import fits
from collections import defaultdict, Counter

__all__ = ["FileGalfit"]

@a99.froze_it
class FileGalfit(DataFile):
    """FITS file with frames named INPUT_*, MODEL_*, RESIDUAL_* (Galfit software output)

    When file is loaded, the band_names property will be filled

    IF INPUT_*, MODEL_* and RESIDUAL_* do not have the same band names, the file is "rejected"
    """
    attrs = []
    default_filename = None
    flag_txt = False

    @property
    def band_names(self):
        return self._band_names

    @property
    def kind_names(self):
        return self._kind_names

    def __init__(self):
        DataFile.__init__(self)
        self.hdulist = None
        self._band_names = []
        self._kind_names = []
        # Frame indexes by key (kind_name, band_name)
        self._idxs = {}

    def get_frame(self, kind_name, band_name):
        """Convenience function to get frame using its "kind name", "band name"

        Args:
            kind_name: str in self.kind_names
            band_name: str in self.band_names
        """
        return self.hdulist[self._idxs[(kind_name, band_name)]]



    def _do_load(self, filename):
        f = fits.open(filename)

        info = f.info(False)


        # Example:
        #     [(0, 'PRIMARY', 'PrimaryHDU', 8, (720, 720), 'float32', ''),
        #      (1, 'INPUT_fuv', 'ImageHDU', 40, (720, 720), 'float64', ''),
        #      (2, 'INPUT_nuv', 'ImageHDU', 40, (720, 720), 'float64', ''),
        #      (3, 'INPUT_r', 'ImageHDU', 42, (720, 720), 'float64', ''),
        #      (4, 'INPUT_j', 'ImageHDU', 41, (720, 720), 'float64', ''),
        #      (5, 'INPUT_h', 'ImageHDU', 41, (720, 720), 'float64', ''),
        #      (6, 'INPUT_k', 'ImageHDU', 41, (720, 720), 'float64', ''),
        #      (7, 'INPUT_3.4', 'ImageHDU', 35, (720, 720), 'float64', ''),
        #      (8, 'INPUT_4.6', 'ImageHDU', 35, (720, 720), 'float64', ''),
        #      (9, 'MODEL_fuv', 'ImageHDU', 409, (720, 720), 'float32', ''),
        #      (10, 'MODEL_nuv', 'ImageHDU', 409, (720, 720), 'float32', '')
        #      .
        #      .
        #      .


        group_names = ("INPUT", "MODEL", "RESIDUAL")
        band_names = defaultdict(lambda: [])  # band names per group
        idxs = {}

        # ***First iteration over frames***
        # Determine the band names that are present in all INPUT, MODEL and RESIDUAL
        for record in info[1:]:  # skips "PRIMARY"
            index = record[0]
            name = record[1]
            if name.startswith(group_names):
                group_name, band_name = name.split("_")
                band_names[group_name].append(band_name)

        # Validation: must find at least one frame for each group
        if len(band_names) != len(group_names):
            raise RuntimeError("Not all groups {} present in file".format(str(group_names)))

        # minimal set of bands present in all groups
        minimal_band_names = set.intersection(*[set(x) for x in band_names.values()])

        # Validation: we want at least one band common to all groups
        if len(minimal_band_names) == 0:
            raise RuntimeError("No common bands for groups {}".format(str(group_names)))

        # ***Second iteration over frames***
        # Generate the index dictionary
        for record in info[1:]:
            index = record[0]
            name = record[1]
            if name.startswith(group_names):
                group_name, band_name = name.split("_")
                if band_name in minimal_band_names:
                    idxs[(group_name, band_name)] = index

        self._band_names = band_names["INPUT"]
        self._kind_names = group_names
        self._idxs = idxs

        self.hdulist = f

    def _do_save_as(self, filename):
        a99.overwrite_fits(self.hdulist, filename)
