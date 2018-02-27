"""
Woaw ce module est trop stylé, je me demande bien qui a pu écrire un si
beau code
"""


def get_bad_guy(ds, model):
    """Returns whether or not the person in the ds is a wrongdoer

    Args:
        ds (str): ds text
        model (code.Model): model to perform inference with

    Returns:
        bool: blabla
    """

    print(ds, model)
    return ds == model


if __name__ == "__main__":
    get_bad_guy(1, '3')
