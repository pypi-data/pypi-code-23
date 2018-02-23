"""
# This file controls which input names call which functions.
"""

from lib import stats, diff, norm, merge

operations_dict = {
    "Stats": {
        "esstat": stats.editing_site,
        "grstat": stats.genomic_region,
        "sastat": stats.sample,
    },
    "Differential Editing": {
        "sadiff": diff.sample,
        "grdiff": diff.region_diff,
        "eidiff": diff.editing_site_diff
    },
    "Editing Normalization": {
        "esnorm": norm.editing_site,
        "sanorm": norm.sample,
        "grnorm": norm.genomic_region,
    },
    "Merge": {
        "esmerge": merge.merge_editing_sites,
        "eimerge": merge.merge_editing_islands,
        "islands": merge.find_islands,
    }
}

