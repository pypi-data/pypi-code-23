

def save_db(db_obj, fname):
    """Save the database.
    Args:
        db_obj: Instance of type IndexStructurePacked or IndexStructureGapped.

        fname: File name (string) of save file.

    Returns:
        -
    """

    import pickle

    with open(fname, 'wb') as file:
            
        pickle.dump(db_obj, file)


def load_db(fname):
    """Load a database.
    Args:
        fname: File name (string) of database previously saved with save_db().

    Returns:

        The saved database instance.

    """

    import pickle

    with open(fname, 'rb') as file:

        return pickle.load(file)
