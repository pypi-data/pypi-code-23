# -*- coding: utf-8 -*-
def normalize_hpo_id(hpo_term):
    """Reformat HPO Term to database Id

    Arguments:
        hpo_term (str): HPO Term

    Returns:
        int: HPO database Id
    """
    if hpo_term.startswith('HP:'):
        hpo_id = hpo_term.lstrip('HP:')
    else:
        hpo_id = hpo_term

    return int(hpo_id.lstrip('0'))
